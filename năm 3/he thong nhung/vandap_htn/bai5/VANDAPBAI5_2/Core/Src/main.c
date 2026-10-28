#include "main.h"
#include <stdio.h>

/* 1: 5 muc PWM; 0: PWM lien tuc */
#define PWM_STEPS  1
#define PWM_MAX    1000U

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
static uint32_t PWM_FromADC(uint16_t adc, uint32_t *percent);

int main(void)
{
    char line[32];
    uint16_t adc;
    uint32_t voltage_mv;
    uint32_t pwm;
    uint32_t percent;

    HAL_Init();
    SystemClock_Config();

    MX_ADC1_Init();
    MX_TIM2_Init();
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

        pwm = PWM_FromADC(adc, &percent);
        __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_2, pwm);

        snprintf(line, sizeof(line), "LED:%3lu%% BT2",
                 (unsigned long)percent);
        LCD_Line(1U, line);

        snprintf(line, sizeof(line), "ADC:%4u %lu.%03luV",
                 (unsigned int)adc,
                 (unsigned long)(voltage_mv / 1000U),
                 (unsigned long)(voltage_mv % 1000U));
        LCD_Line(0U, line);

        HAL_Delay(200U);
    }
}

/*
 * Mach hien tai: 3.3V -> LDR -> PA0 -> 10k -> GND.
 * Cang sang: ADC cang cao.
 * Dao ADC de cang toi: LED cang sang.
 */
static uint32_t PWM_FromADC(uint16_t adc, uint32_t *percent)
{
    uint32_t adc_dark = 4095U - (uint32_t)adc;

#if PWM_STEPS == 1
    if (adc_dark < 819U)
        *percent = 0U;
    else if (adc_dark < 1638U)
        *percent = 25U;
    else if (adc_dark < 2457U)
        *percent = 50U;
    else if (adc_dark < 3276U)
        *percent = 75U;
    else
        *percent = 100U;

    return (*percent * PWM_MAX) / 100U;
#else
    uint32_t pwm = (adc_dark * PWM_MAX) / 4095U;
    *percent = (pwm * 100U) / PWM_MAX;
    return pwm;
#endif
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

    HAL_GPIO_WritePin(GPIOB, LCD_D4,
                     (nibble & 1U) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOB, LCD_D5,
                     (nibble & 2U) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOB, LCD_D6,
                     (nibble & 4U) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOB, LCD_D7,
                     (nibble & 8U) ? GPIO_PIN_SET : GPIO_PIN_RESET);

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

    LCD_Command(0x28U);
    LCD_Command(0x08U);
    LCD_Command(0x01U);
    LCD_Command(0x06U);
    LCD_Command(0x0CU);
}

static void LCD_Line(uint8_t row, const char *text)
{
    LCD_Command((row == 0U) ? 0x80U : 0xC0U);

    for (uint8_t i = 0U; i < 16U; ++i)
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

    clk.ClockType = RCC_CLOCKTYPE_SYSCLK |
                    RCC_CLOCKTYPE_HCLK |
                    RCC_CLOCKTYPE_PCLK1 |
                    RCC_CLOCKTYPE_PCLK2;
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

    if (HAL_TIM_PWM_ConfigChannel(&htim2, &output,
                                 TIM_CHANNEL_2) != HAL_OK)
        Error_Handler();
}

static void MX_GPIO_Init(void)
{
    GPIO_InitTypeDef gpio = {0};

    __HAL_RCC_AFIO_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_AFIO_REMAP_TIM2_DISABLE();

    /* PA0: ADC */
    gpio.Pin = GPIO_PIN_0;
    gpio.Mode = GPIO_MODE_ANALOG;
    HAL_GPIO_Init(GPIOA, &gpio);

    /* PA1: TIM2 Channel 2 PWM */
    gpio.Pin = GPIO_PIN_1;
    gpio.Mode = GPIO_MODE_AF_PP;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOA, &gpio);

    /* LCD: PB0, PB1, PB10, PB11, PB12, PB13 */
    HAL_GPIO_WritePin(GPIOB, LCD_ALL, GPIO_PIN_RESET);

    gpio.Pin = LCD_ALL;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOB, &gpio);
}

void Error_Handler(void)
{
    __disable_irq();

    while (1)
    {
    }
}

#ifdef USE_FULL_ASSERT
void assert_failed(uint8_t *file, uint32_t line)
{
    (void)file;
    (void)line;
    Error_Handler();
}
#endif
