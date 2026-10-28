/* Complete main.c: PA0-PA7 LEDs (LOW = ON).
 * Buttons PB0, PB1, PB2, PB3 to GND, internal pull-up.
 * HSI 8 MHz. Replace Core/Src/main.c in a generated STM32F1 HAL project.
 */
#include "main.h"

#define LED_MASK ((uint16_t)0x00FFU)
#define BUTTON_MASK (GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3)
#define DEBOUNCE_MS 30U
#define STEP_MS 1000U

static uint8_t sequence = 0;
static uint8_t next_led = 0;
static uint32_t step_tick = 0;

void SystemClock_Config(void);
static void MX_GPIO_Init(void);
void Mode1_Even(void);
void Mode2_Odd(void);
void Mode3_OnSequence(void);
void Mode4_OffSequence(void);
static void UpdateSequence(void);
static uint8_t ReadButtonEvents(void);

int main(void)
{
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();

  while (1)
  {
    uint8_t events = ReadButtonEvents();
    /* If pressed together, priority is PB0, PB1, PB2, PB3. */
    if (events & 0x01U)      Mode1_Even();
    else if (events & 0x02U) Mode2_Odd();
    else if (events & 0x04U) Mode3_OnSequence();
    else if (events & 0x08U) Mode4_OffSequence();

    UpdateSequence();
    HAL_Delay(1);
  }
}

/* PB0: PA0, PA2, PA4, PA6 ON; others OFF. */
void Mode1_Even(void)
{
  sequence = 0;
  HAL_GPIO_WritePin(GPIOA, LED_MASK, GPIO_PIN_SET);
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_0 | GPIO_PIN_2 |
                          GPIO_PIN_4 | GPIO_PIN_6, GPIO_PIN_RESET);
}

/* PB1: PA1, PA3, PA5, PA7 ON; others OFF. */
void Mode2_Odd(void)
{
  sequence = 0;
  HAL_GPIO_WritePin(GPIOA, LED_MASK, GPIO_PIN_SET);
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_1 | GPIO_PIN_3 |
                          GPIO_PIN_5 | GPIO_PIN_7, GPIO_PIN_RESET);
}

/* PB2: start all OFF, turn PA0 ON immediately, then PA1..PA7. */
void Mode3_OnSequence(void)
{
  HAL_GPIO_WritePin(GPIOA, LED_MASK, GPIO_PIN_SET);
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_0, GPIO_PIN_RESET);
  sequence = 1;
  next_led = 1;
  step_tick = HAL_GetTick();
}

/* PB3: start all ON, turn PA0 OFF immediately, then PA1..PA7. */
void Mode4_OffSequence(void)
{
  HAL_GPIO_WritePin(GPIOA, LED_MASK, GPIO_PIN_RESET);
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_0, GPIO_PIN_SET);
  sequence = 2;
  next_led = 1;
  step_tick = HAL_GetTick();
}

static void UpdateSequence(void)
{
  uint32_t now = HAL_GetTick();
  if (sequence == 0 || (uint32_t)(now - step_tick) < STEP_MS)
    return;

  step_tick = now;
  HAL_GPIO_WritePin(GPIOA, (uint16_t)(1U << next_led),
                    sequence == 1 ? GPIO_PIN_RESET : GPIO_PIN_SET);
  next_led++;
  if (next_led >= 8U)
    sequence = 0;
}

/* Independent debounce, one event per press; release before pressing again. */
static uint8_t ReadButtonEvents(void)
{
  static uint8_t raw_prev[4] = {1, 1, 1, 1};
  static uint8_t stable[4] = {1, 1, 1, 1};
  static uint32_t changed_tick[4] = {0, 0, 0, 0};
  uint32_t now = HAL_GetTick();
  uint8_t events = 0;
  const uint16_t button_pins[4] = {
    GPIO_PIN_0, GPIO_PIN_1, GPIO_PIN_2, GPIO_PIN_3
  };

  for (uint8_t i = 0; i < 4; i++)
  {
    uint8_t raw = HAL_GPIO_ReadPin(GPIOB, button_pins[i])
                  == GPIO_PIN_SET ? 1U : 0U;
    if (raw != raw_prev[i])
    {
      raw_prev[i] = raw;
      changed_tick[i] = now;
    }
    if (raw != stable[i] &&
        (uint32_t)(now - changed_tick[i]) >= DEBOUNCE_MS)
    {
      stable[i] = raw;
      if (raw == 0U)
        events |= (uint8_t)(1U << i);
    }
  }
  return events;
}

void SystemClock_Config(void)
{
  RCC_OscInitTypeDef osc = {0};
  RCC_ClkInitTypeDef clk = {0};
  osc.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  osc.HSIState = RCC_HSI_ON;
  osc.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  osc.PLL.PLLState = RCC_PLL_NONE;
  if (HAL_RCC_OscConfig(&osc) != HAL_OK) Error_Handler();

  clk.ClockType = RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_HCLK |
                 RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
  clk.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
  clk.AHBCLKDivider = RCC_SYSCLK_DIV1;
  clk.APB1CLKDivider = RCC_HCLK_DIV1;
  clk.APB2CLKDivider = RCC_HCLK_DIV1;
  if (HAL_RCC_ClockConfig(&clk, FLASH_LATENCY_0) != HAL_OK)
    Error_Handler();
}

static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef gpio = {0};
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();
  __HAL_RCC_AFIO_CLK_ENABLE();

  /* Release PB3/PB4 from JTAG; retain SWD on PA13/PA14. */
  __HAL_AFIO_REMAP_SWJ_NOJTAG();

  HAL_GPIO_WritePin(GPIOA, LED_MASK, GPIO_PIN_SET);
  gpio.Pin = LED_MASK;
  gpio.Mode = GPIO_MODE_OUTPUT_PP;
  gpio.Pull = GPIO_NOPULL;
  gpio.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &gpio);

  gpio.Pin = BUTTON_MASK;
  gpio.Mode = GPIO_MODE_INPUT;
  gpio.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(GPIOB, &gpio);
}

void Error_Handler(void)
{
  __disable_irq();
  while (1) { }
}

#ifdef USE_FULL_ASSERT
void assert_failed(uint8_t *file, uint32_t line)
{
  (void)file;
  (void)line;
}
#endif
