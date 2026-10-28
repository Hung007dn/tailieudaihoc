/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : LDR - 3 LED - Button - UART
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc1;
UART_HandleTypeDef huart1;

/* USER CODE BEGIN PV */
uint32_t adc_value = 0;
uint8_t mode = 0;
uint8_t uart_rx = 0;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_ADC1_Init(void);
static void MX_USART1_UART_Init(void);

/* USER CODE BEGIN PFP */
void UART_SendString(char *str);
void UART_SendNumber(uint32_t num);

void LED_AllOff(void);
void LED_AllOn(void);

void LED_GreenOn(void);
void LED_YellowOn(void);
void LED_RedOn(void);
/* USER CODE END PFP */

/* USER CODE BEGIN 0 */

void UART_SendString(char *str)
{
    while (*str)
    {
        HAL_UART_Transmit(&huart1, (uint8_t *)str, 1, 100);
        str++;
    }
}

void UART_SendNumber(uint32_t num)
{
    char buf[12];
    uint8_t i = 0;

    if (num == 0)
    {
        UART_SendString("0");
        return;
    }

    while (num > 0)
    {
        buf[i++] = (num % 10) + '0';
        num /= 10;
    }

    while (i > 0)
    {
        i--;

        HAL_UART_Transmit(
            &huart1,
            (uint8_t *)&buf[i],
            1,
            100
        );
    }
}


/* =========================================================
   LED ACTIVE-HIGH (anode noi GPIO, cathode noi GND)
   SET   = SANG
   RESET = TAT
   ========================================================= */

void LED_AllOff(void)
{
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_3, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET);
}

void LED_AllOn(void)
{
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2, GPIO_PIN_SET);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_3, GPIO_PIN_SET);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET);
}

void LED_GreenOn(void)
{
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_3, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET);
}

void LED_YellowOn(void)
{
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_3, GPIO_PIN_SET);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET);
}

void LED_RedOn(void)
{
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2, GPIO_PIN_SET);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_3, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET);
}

/* USER CODE END 0 */


/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
    HAL_Init();

    SystemClock_Config();

    MX_GPIO_Init();
    MX_ADC1_Init();
    MX_USART1_UART_Init();

    /* USER CODE BEGIN 2 */

    /* Proteus STM32 model may not complete the F1 ADC calibration cycle,
     * which blocks execution before the first UART message. The simulated
     * ADC works without this hardware-only calibration step. */
    /* HAL_ADCEx_Calibration_Start(&hadc1); */

    HAL_ADC_Start(&hadc1);

    /* Luc khoi dong: tat het LED */
    LED_AllOff();

    UART_SendString("\r\n");
    UART_SendString("====================================\r\n");
    UART_SendString("      LDR LED CONTROL SYSTEM\r\n");
    UART_SendString("====================================\r\n");
    UART_SendString("MODE 0 = OFF\r\n");
    UART_SendString("MODE 1 = AUTO\r\n");
    UART_SendString("MODE 2 = ON\r\n");
    UART_SendString("TYPE 0, 1 OR 2 TO SELECT MODE\r\n");
    UART_SendString("====================================\r\n");

    /* USER CODE END 2 */

    uint32_t last_uart_time = 0;
    uint8_t send_uart = 0;

    while (1)
    {
        /* =====================================================
         * 1. DOC ADC TU LDR
         * ===================================================== */

        if (HAL_ADC_PollForConversion(&hadc1, 100) == HAL_OK)
        {
            adc_value = HAL_ADC_GetValue(&hadc1);
        }

        /* Chon truc tiep MODE 0, 1 hoac 2 tu Virtual Terminal. */
        if (HAL_UART_Receive(&huart1, &uart_rx, 1, 0) == HAL_OK)
        {
            if ((uart_rx >= '0') && (uart_rx <= '2'))
            {
                mode = uart_rx - '0';

                UART_SendString("\r\n>>> UART SELECT MODE: ");
                UART_SendNumber(mode);
                UART_SendString(" <<<\r\n");
            }
        }


        /* =====================================================
         * 2. DOC NUT NHAN PB0
         *
         * PB0 co pull-up:
         * Khong nhan = HIGH
         * Nhan       = LOW
         * ===================================================== */

        if (HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_0) == GPIO_PIN_RESET)
        {
            HAL_Delay(20);

            if (HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_0) == GPIO_PIN_RESET)
            {
                mode++;

                if (mode > 2)
                {
                    mode = 0;
                }

                UART_SendString("\r\n>>> CHANGE MODE: ");

                UART_SendNumber(mode);

                UART_SendString(" <<<\r\n");

                /* Cho den khi tha nut */
                while (HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_0)
                        == GPIO_PIN_RESET)
                {
                    HAL_Delay(10);
                }
            }
        }

        /* Quet nut moi 10 ms, nhung chi gui bao cao UART moi 300 ms. */
        send_uart = 0;
        if ((HAL_GetTick() - last_uart_time) >= 300)
        {
            last_uart_time = HAL_GetTick();
            send_uart = 1;
        }


        /* =====================================================
         * MODE 0 - OFF
         * LED LUON TAT
         * ===================================================== */

        if (mode == 0)
        {
            LED_AllOff();

            if (send_uart)
            {
                UART_SendString("ADC=");
                UART_SendNumber(adc_value);

                UART_SendString(
                    " | MODE=0 OFF"
                    " | LED=ALL OFF\r\n"
                );
            }
        }


        /* =====================================================
         * MODE 1 - AUTO
         * ===================================================== */

        else if (mode == 1)
        {
            /*
             * Mach:
             *
             * 3.3V
             *  |
             * 10K
             *  |
             *  +------ PA1 (ADC1_IN1)
             *  |
             * LDR
             *  |
             * GND
             *
             * Sang manh -> ADC thap
             * Toi       -> ADC cao
             */


            /* ----------------------------------------
             * BRIGHT
             * ADC < 1400
             * LED XANH SANG
             * ---------------------------------------- */

            if (adc_value < 1400)
            {
                LED_GreenOn();

                if (send_uart)
                {
                    UART_SendString("ADC=");
                    UART_SendNumber(adc_value);

                    UART_SendString(
                        " | MODE=1 AUTO"
                        " | LIGHT=BRIGHT"
                        " | GREEN ON\r\n"
                    );
                }
            }


            /* ----------------------------------------
             * NORMAL
             * 1400 <= ADC < 2800
             * LED VANG SANG
             * ---------------------------------------- */

            else if (adc_value < 2800)
            {
                LED_YellowOn();

                if (send_uart)
                {
                    UART_SendString("ADC=");
                    UART_SendNumber(adc_value);

                    UART_SendString(
                        " | MODE=1 AUTO"
                        " | LIGHT=NORMAL"
                        " | YELLOW ON\r\n"
                    );
                }
            }


            /* ----------------------------------------
             * DARK
             * ADC >= 2800
             * LED DO SANG
             * ---------------------------------------- */

            else
            {
                LED_RedOn();

                if (send_uart)
                {
                    UART_SendString("ADC=");
                    UART_SendNumber(adc_value);

                    UART_SendString(
                        " | MODE=1 AUTO"
                        " | LIGHT=DARK"
                        " | RED ON\r\n"
                    );
                }
            }
        }


        /* =====================================================
         * MODE 2 - ON
         * CA 3 LED LUON SANG
         * ===================================================== */

        else
        {
            LED_AllOn();

            if (send_uart)
            {
                UART_SendString("ADC=");
                UART_SendNumber(adc_value);

                UART_SendString(
                    " | MODE=2 ON"
                    " | LED=ALL ON\r\n"
                );
            }
        }


        HAL_Delay(10);
    }
}


/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
    RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

    RCC_OscInitStruct.OscillatorType =
        RCC_OSCILLATORTYPE_HSI;

    RCC_OscInitStruct.HSIState =
        RCC_HSI_ON;

    RCC_OscInitStruct.HSICalibrationValue =
        RCC_HSICALIBRATION_DEFAULT;

    RCC_OscInitStruct.PLL.PLLState =
        RCC_PLL_NONE;

    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
    {
        Error_Handler();
    }

    RCC_ClkInitStruct.ClockType =
        RCC_CLOCKTYPE_HCLK |
        RCC_CLOCKTYPE_SYSCLK |
        RCC_CLOCKTYPE_PCLK1 |
        RCC_CLOCKTYPE_PCLK2;

    RCC_ClkInitStruct.SYSCLKSource =
        RCC_SYSCLKSOURCE_HSI;

    RCC_ClkInitStruct.AHBCLKDivider =
        RCC_SYSCLK_DIV1;

    RCC_ClkInitStruct.APB1CLKDivider =
        RCC_HCLK_DIV1;

    RCC_ClkInitStruct.APB2CLKDivider =
        RCC_HCLK_DIV1;

    if (HAL_RCC_ClockConfig(
            &RCC_ClkInitStruct,
            FLASH_LATENCY_0) != HAL_OK)
    {
        Error_Handler();
    }

    PeriphClkInit.PeriphClockSelection =
        RCC_PERIPHCLK_ADC;

    PeriphClkInit.AdcClockSelection =
        RCC_ADCPCLK2_DIV2;

    if (HAL_RCCEx_PeriphCLKConfig(
            &PeriphClkInit) != HAL_OK)
    {
        Error_Handler();
    }
}


/**
  * @brief ADC1 Initialization Function
  */
static void MX_ADC1_Init(void)
{
    ADC_ChannelConfTypeDef sConfig = {0};

    hadc1.Instance = ADC1;

    hadc1.Init.ScanConvMode =
        ADC_SCAN_DISABLE;

    hadc1.Init.ContinuousConvMode =
        ENABLE;

    hadc1.Init.DiscontinuousConvMode =
        DISABLE;

    hadc1.Init.ExternalTrigConv =
        ADC_SOFTWARE_START;

    hadc1.Init.DataAlign =
        ADC_DATAALIGN_RIGHT;

    hadc1.Init.NbrOfConversion =
        1;

    if (HAL_ADC_Init(&hadc1) != HAL_OK)
    {
        Error_Handler();
    }

    sConfig.Channel =
        ADC_CHANNEL_1;

    sConfig.Rank =
        ADC_REGULAR_RANK_1;

    sConfig.SamplingTime =
        ADC_SAMPLETIME_55CYCLES_5;

    if (HAL_ADC_ConfigChannel(
            &hadc1,
            &sConfig) != HAL_OK)
    {
        Error_Handler();
    }
}


/**
  * @brief USART1 Initialization Function
  */
static void MX_USART1_UART_Init(void)
{
    huart1.Instance = USART1;

    huart1.Init.BaudRate =
        9600;

    huart1.Init.WordLength =
        UART_WORDLENGTH_8B;

    huart1.Init.StopBits =
        UART_STOPBITS_1;

    huart1.Init.Parity =
        UART_PARITY_NONE;

    huart1.Init.Mode =
        UART_MODE_TX_RX;

    huart1.Init.HwFlowCtl =
        UART_HWCONTROL_NONE;

    huart1.Init.OverSampling =
        UART_OVERSAMPLING_16;

    if (HAL_UART_Init(&huart1) != HAL_OK)
    {
        Error_Handler();
    }
}


/**
  * @brief GPIO Initialization Function
  */
static void MX_GPIO_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();


    /* =====================================================
     * MAC DINH TAT 3 LED
     *
     * Active-high:
     * RESET = TAT
     * ===================================================== */

    HAL_GPIO_WritePin(
        GPIOA,
        GPIO_PIN_2 |
        GPIO_PIN_3 |
        GPIO_PIN_4,
        GPIO_PIN_RESET
    );


    /* =====================================================
     * PB0 - BUTTON
     * ===================================================== */

    GPIO_InitStruct.Pin =
        GPIO_PIN_0;

    GPIO_InitStruct.Mode =
        GPIO_MODE_INPUT;

    GPIO_InitStruct.Pull =
        GPIO_PULLUP;

    HAL_GPIO_Init(
        GPIOB,
        &GPIO_InitStruct
    );


    /* =====================================================
     * PA2 PA3 PA4 - RED YELLOW GREEN LED OUTPUT
     * ===================================================== */

    GPIO_InitStruct.Pin =
        GPIO_PIN_2 |
        GPIO_PIN_3 |
        GPIO_PIN_4;

    GPIO_InitStruct.Mode =
        GPIO_MODE_OUTPUT_PP;

    GPIO_InitStruct.Pull =
        GPIO_NOPULL;

    GPIO_InitStruct.Speed =
        GPIO_SPEED_FREQ_LOW;

    HAL_GPIO_Init(
        GPIOA,
        &GPIO_InitStruct
    );
}


/**
  * @brief Error Handler
  */
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
}

#endif
