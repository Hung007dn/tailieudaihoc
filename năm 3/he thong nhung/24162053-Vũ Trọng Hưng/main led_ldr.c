/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : LDR ADC + LED + UART
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdio.h>
#include <string.h>
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define LDR_THRESHOLD 2000
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc1;
UART_HandleTypeDef huart1;

/* USER CODE BEGIN PV */
uint32_t adc_value = 0;
char msg[100];
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_ADC1_Init(void);
static void MX_USART1_UART_Init(void);

/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

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

  /* LED OFF lúc khởi động */
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2, GPIO_PIN_SET);

  /* Kiểm tra UART */
  char start_msg[] = "SYSTEM START\r\n";

  HAL_UART_Transmit(&huart1,
                    (uint8_t *)start_msg,
                    strlen(start_msg),
                    HAL_MAX_DELAY);

  while (1)
  {
    /* Bắt đầu chuyển đổi ADC */
    HAL_ADC_Start(&hadc1);

    /* Chờ ADC chuyển đổi xong */
    if (HAL_ADC_PollForConversion(&hadc1, 100) == HAL_OK)
    {
      /* Đọc giá trị ADC */
      adc_value = HAL_ADC_GetValue(&hadc1);

      /*
       * LED của mạch đang nối:
       *
       * VCC -> R -> LED -> PA2
       *
       * PA2 = RESET -> LED ON
       * PA2 = SET   -> LED OFF
       */

      if (adc_value > LDR_THRESHOLD)
      {
        HAL_GPIO_WritePin(GPIOA,
                          GPIO_PIN_2,
                          GPIO_PIN_RESET);

        sprintf(msg,
                "LDR ADC = %lu | LED = ON\r\n",
                adc_value);
      }
      else
      {
        HAL_GPIO_WritePin(GPIOA,
                          GPIO_PIN_2,
                          GPIO_PIN_SET);

        sprintf(msg,
                "LDR ADC = %lu | LED = OFF\r\n",
                adc_value);
      }

      /* Gửi ra Virtual Terminal */
      HAL_UART_Transmit(&huart1,
                        (uint8_t *)msg,
                        strlen(msg),
                        HAL_MAX_DELAY);
    }

    HAL_ADC_Stop(&hadc1);

    HAL_Delay(500);
  }
}

/**
  * @brief ADC1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC1_Init(void)
{
  ADC_ChannelConfTypeDef sConfig = {0};

  hadc1.Instance = ADC1;

  hadc1.Init.ScanConvMode = ADC_SCAN_DISABLE;

  hadc1.Init.ContinuousConvMode = DISABLE;

  hadc1.Init.DiscontinuousConvMode = DISABLE;

  hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;

  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;

  hadc1.Init.NbrOfConversion = 1;

  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }

  /* PA1 = ADC1_IN1 */
  sConfig.Channel = ADC_CHANNEL_1;

  sConfig.Rank = ADC_REGULAR_RANK_1;

  sConfig.SamplingTime = ADC_SAMPLETIME_55CYCLES_5;

  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief USART1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART1_UART_Init(void)
{
  huart1.Instance = USART1;

  huart1.Init.BaudRate = 115200;

  huart1.Init.WordLength = UART_WORDLENGTH_8B;

  huart1.Init.StopBits = UART_STOPBITS_1;

  huart1.Init.Parity = UART_PARITY_NONE;

  huart1.Init.Mode = UART_MODE_TX_RX;

  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;

  huart1.Init.OverSampling = UART_OVERSAMPLING_16;

  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  __HAL_RCC_GPIOA_CLK_ENABLE();

  /*
   * PA2 = LED
   * LED active LOW
   */
  HAL_GPIO_WritePin(GPIOA,
                    GPIO_PIN_2,
                    GPIO_PIN_SET);

  GPIO_InitStruct.Pin = GPIO_PIN_2;

  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;

  GPIO_InitStruct.Pull = GPIO_NOPULL;

  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;

  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
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

  /*
   * Dùng HSI 8 MHz
   * Không phụ thuộc thạch anh ngoài khi mô phỏng Proteus
   */

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

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct,
                          FLASH_LATENCY_0) != HAL_OK)
  {
    Error_Handler();
  }

  /*
   * ADC Clock
   * PCLK2 = 8 MHz
   * ADC clock = 8 / 6 = 1.333 MHz
   */

  PeriphClkInit.PeriphClockSelection =
      RCC_PERIPHCLK_ADC;

  PeriphClkInit.AdcClockSelection =
      RCC_ADCPCLK2_DIV6;

  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief Error Handler
  * @retval None
  */
void Error_Handler(void)
{
  __disable_irq();

  while (1)
  {
  }
}

#ifdef USE_FULL_ASSERT

/**
  * @brief Reports assert error
  */
void assert_failed(uint8_t *file, uint32_t line)
{
}

#endif
