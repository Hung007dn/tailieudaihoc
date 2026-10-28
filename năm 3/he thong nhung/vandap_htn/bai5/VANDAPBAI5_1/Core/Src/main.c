/* STM32F103C6 - Proteus: LDR + LCD 16x2 + LED.
 * Replace Core/Src/main.c in a CubeIDE HAL project.
 * Enable ADC1 IN0 and TIM2 PWM CH2 in CubeMX before generation.
 * Generate peripheral initialization in main.c, not separate adc.c/tim.c.
 * HSI/SYSCLK = 8 MHz; TIM2 PWM = 1 kHz; ADC clock = 4 MHz.
 * PA0: 3.3V -> LDR -> PA0 -> 10k -> GND (dark = higher ADC).
 * PA1 -> 330 ohm -> LED anode; LED cathode -> GND.
 * LCD: RS=PB0, E=PB1, D4=PB10, D5=PB11, D6=PB12, D7=PB13.
 * LCD VSS/RW=GND, VDD=5V, V0=10k contrast potentiometer wiper.
 * Common ground for all supplies. MCU VDDA/VDD=3.3V, VSSA/VSS=GND.
 */
#include "main.h"
#include <stdio.h>

/* Change only these settings to choose the exercise. */
#define APP_EXERCISE       1   /* 1: LCD + ON/OFF; 2: LCD + PWM */
#define PWM_STEPS          1   /* 1: 0/25/50/75/100%; 0: continuous */
#define LED_ON_THRESHOLD   2048U /* Example threshold, adjustable */
#define PWM_MAX            1000U /* ARR=999; CCR=1000 gives 100% */

#if APP_EXERCISE != 1 && APP_EXERCISE != 2
#error "APP_EXERCISE must be 1 or 2"
#endif
#if PWM_STEPS != 0 && PWM_STEPS != 1
#error "PWM_STEPS must be 0 or 1"
#endif

#define LCD_RS GPIO_PIN_0
#define LCD_EN GPIO_PIN_1
#define LCD_D4 GPIO_PIN_10
#define LCD_D5 GPIO_PIN_11
#define LCD_D6 GPIO_PIN_12
#define LCD_D7 GPIO_PIN_13
#define LCD_ALL (LCD_RS | LCD_EN | LCD_D4 | LCD_D5 | LCD_D6 | LCD_D7)

ADC_HandleTypeDef hadc1;
TIM_HandleTypeDef htim2;

void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_ADC1_Init(void);
static void MX_TIM2_Init(void);
static void LCD_Init(void);
static void LCD_Line(uint8_t row, const char *text);
static uint16_t ADC_Read(void);

int main(void)
{
    char line[32];
    uint16_t adc;
    uint32_t voltage_mv;
    uint32_t pwm;
#if APP_EXERCISE == 2
    uint32_t percent;
#endif

    HAL_Init();
    SystemClock_Config();
    MX_ADC1_Init();
    MX_TIM2_Init();
    /* Apply the intended GPIO modes after all peripheral MSP functions. */
    MX_GPIO_Init();

    if (HAL_ADCEx_Calibration_Start(&hadc1) != HAL_OK)
        Error_Handler();
    if (HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_2) != HAL_OK)
        Error_Handler();

    LCD_Init();

    while (1)
    {
        adc = ADC_Read();
        voltage_mv = ((uint32_t)adc * 3300U) / 4095U;

#if APP_EXERCISE == 1
        pwm = (adc >= LED_ON_THRESHOLD) ? PWM_MAX : 0U;
        __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_2, pwm);
        snprintf(line, sizeof(line), "LED:%s  BT1",
                 (pwm != 0U) ? "ON" : "OFF");
#else
#if PWM_STEPS == 1
        /* Five example ADC bands; tune for the chosen LDR model. */
        if      (adc < 819U)  percent = 0U;
        else if (adc < 1638U) percent = 25U;
        else if (adc < 2457U) percent = 50U;
        else if (adc < 3276U) percent = 75U;
        else                 percent = 100U;
        pwm = (percent * PWM_MAX) / 100U;
#else
        /* Continuous formula specified in the exercise. */
        pwm = ((uint32_t)adc * PWM_MAX) / 4095U;
        percent = (pwm * 100U) / PWM_MAX;
#endif
        __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_2, pwm);
        snprintf(line, sizeof(line), "LED:%3lu%% BT2",
                 (unsigned long)percent);
#endif
        LCD_Line(1U, line);
        snprintf(line, sizeof(line), "ADC:%4u %lu.%03luV",
                 (unsigned int)adc,
                 (unsigned long)(voltage_mv / 1000U),
                 (unsigned long)(voltage_mv % 1000U));
        LCD_Line(0U, line);
        HAL_Delay(200U);
    }
}

static uint16_t ADC_Read(void)
{
    uint16_t value;
    if (HAL_ADC_Start(&hadc1) != HAL_OK)
        Error_Handler();
    if (HAL_ADC_PollForConversion(&hadc1, 100U) != HAL_OK)
        Error_Handler();
    value = (uint16_t)HAL_ADC_GetValue(&hadc1);
    if (HAL_ADC_Stop(&hadc1) != HAL_OK)
        Error_Handler();
    return value;
}

static void LCD_Nibble(uint8_t nibble)
{
    HAL_GPIO_WritePin(GPIOB, LCD_EN, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOB, LCD_D4, (nibble & 1U) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOB, LCD_D5, (nibble & 2U) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOB, LCD_D6, (nibble & 4U) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOB, LCD_D7, (nibble & 8U) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_Delay(1U);
    HAL_GPIO_WritePin(GPIOB, LCD_EN, GPIO_PIN_SET);
    HAL_Delay(1U);
    HAL_GPIO_WritePin(GPIOB, LCD_EN, GPIO_PIN_RESET);
    HAL_Delay(1U);
}

static void LCD_Send(uint8_t value, GPIO_PinState rs)
{
    HAL_GPIO_WritePin(GPIOB, LCD_RS, rs);
    LCD_Nibble(value >> 4U);
    LCD_Nibble(value & 0x0FU);
}

static void LCD_Command(uint8_t command)
{
    LCD_Send(command, GPIO_PIN_RESET);
    if (command == 0x01U || command == 0x02U)
        HAL_Delay(3U);
}

static void LCD_Init(void)
{
    HAL_GPIO_WritePin(GPIOB, LCD_RS | LCD_EN, GPIO_PIN_RESET);
    HAL_Delay(50U);
    LCD_Nibble(0x03U);
    HAL_Delay(5U);
    LCD_Nibble(0x03U);
    HAL_Delay(5U);
    LCD_Nibble(0x03U);
    HAL_Delay(1U);
    LCD_Nibble(0x02U);
    LCD_Command(0x28U); /* 4-bit interface, two lines */
    LCD_Command(0x08U); /* Display off during initialization */
    LCD_Command(0x01U); /* Clear */
    LCD_Command(0x06U); /* Increment cursor */
    LCD_Command(0x0CU); /* Display on, cursor off */
}

static void LCD_Line(uint8_t row, const char *text)
{
    uint8_t i;
    LCD_Command((row == 0U) ? 0x80U : 0xC0U);
    for (i = 0U; i < 16U; ++i)
    {
        uint8_t character = (uint8_t)' ';
        if (*text != '\0')
            character = (uint8_t)*text++;
        LCD_Send(character, GPIO_PIN_SET);
    }
}

void SystemClock_Config(void)
{
    RCC_OscInitTypeDef osc = {0};
    RCC_ClkInitTypeDef clk = {0};
    RCC_PeriphCLKInitTypeDef peripheral = {0};

    osc.OscillatorType = RCC_OSCILLATORTYPE_HSI;
    osc.HSIState = RCC_HSI_ON;
    osc.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
    osc.PLL.PLLState = RCC_PLL_NONE;
    if (HAL_RCC_OscConfig(&osc) != HAL_OK)
        Error_Handler();

    clk.ClockType = RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_HCLK |
                    RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    clk.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
    clk.AHBCLKDivider = RCC_SYSCLK_DIV1;
    clk.APB1CLKDivider = RCC_HCLK_DIV1;
    clk.APB2CLKDivider = RCC_HCLK_DIV1;
    if (HAL_RCC_ClockConfig(&clk, FLASH_LATENCY_0) != HAL_OK)
        Error_Handler();

    peripheral.PeriphClockSelection = RCC_PERIPHCLK_ADC;
    peripheral.AdcClockSelection = RCC_ADCPCLK2_DIV2;
    if (HAL_RCCEx_PeriphCLKConfig(&peripheral) != HAL_OK)
        Error_Handler();
}

static void MX_ADC1_Init(void)
{
    ADC_ChannelConfTypeDef channel = {0};
    __HAL_RCC_ADC1_CLK_ENABLE();
    hadc1.Instance = ADC1;
    hadc1.Init.ScanConvMode = ADC_SCAN_DISABLE;
    hadc1.Init.ContinuousConvMode = DISABLE;
    hadc1.Init.DiscontinuousConvMode = DISABLE;
    hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
    hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
    hadc1.Init.NbrOfConversion = 1U;
    if (HAL_ADC_Init(&hadc1) != HAL_OK)
        Error_Handler();
    channel.Channel = ADC_CHANNEL_0;
    channel.Rank = ADC_REGULAR_RANK_1;
    channel.SamplingTime = ADC_SAMPLETIME_239CYCLES_5;
    if (HAL_ADC_ConfigChannel(&hadc1, &channel) != HAL_OK)
        Error_Handler();
}

static void MX_TIM2_Init(void)
{
    TIM_OC_InitTypeDef output = {0};
    __HAL_RCC_TIM2_CLK_ENABLE();
    htim2.Instance = TIM2;
    htim2.Init.Prescaler = 7U;
    htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim2.Init.Period = PWM_MAX - 1U;
    htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
    if (HAL_TIM_PWM_Init(&htim2) != HAL_OK)
        Error_Handler();
    output.OCMode = TIM_OCMODE_PWM1;
    output.Pulse = 0U;
    output.OCPolarity = TIM_OCPOLARITY_HIGH;
    output.OCFastMode = TIM_OCFAST_DISABLE;
    if (HAL_TIM_PWM_ConfigChannel(&htim2, &output, TIM_CHANNEL_2) != HAL_OK)
        Error_Handler();
}

static void MX_GPIO_Init(void)
{
    GPIO_InitTypeDef gpio = {0};
    __HAL_RCC_AFIO_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_AFIO_REMAP_TIM2_DISABLE();

    gpio.Pin = GPIO_PIN_0;
    gpio.Mode = GPIO_MODE_ANALOG;
    HAL_GPIO_Init(GPIOA, &gpio);

    gpio.Pin = GPIO_PIN_1;
    gpio.Mode = GPIO_MODE_AF_PP;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOA, &gpio);

    HAL_GPIO_WritePin(GPIOB, LCD_ALL, GPIO_PIN_RESET);
    gpio.Pin = LCD_ALL;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
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
    Error_Handler();
}
#endif
