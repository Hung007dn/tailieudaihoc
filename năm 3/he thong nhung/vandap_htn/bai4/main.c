/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Bai tap: HE THONG DIEU KHIEN LED 3 CHE DO VOI NUT NHAN VA LDR
  *                   - USART1 : TX (PA9), RX (PA10) @ 9600 bps
  *                   - ADC1   : PA1 (chan 11) noi voi cam bien LDR
  *                   - Nut nhan: PA0 (chan 10) hoac go phim tren Virtual Terminal
  *                   - Den LED:
  *                     + PA2 (chan 12) : LED Do (hoac den LED hien tai tren mach)
  *                     + PA3 (chan 13) : LED Vang (tuy chon them)
  *                     + PA4 (chan 14) : LED Xanh (tuy chon them)
  *                   - Che do:
  *                     + MODE 0 - OFF  : LED luon tat
  *                     + MODE 1 - AUTO : LED tu dong theo LDR (BRIGHT / NORMAL / DARK)
  *                     + MODE 2 - ON   : LED luon sang
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include <stdio.h>
#include <string.h>

/* Types for UART & ADC standard HAL interface */
typedef struct {
  USART_TypeDef *Instance;
} UART_HandleTypeDef;

typedef struct {
  ADC_TypeDef *Instance;
} ADC_HandleTypeDef;

/* Global variables */
UART_HandleTypeDef huart1;
ADC_HandleTypeDef hadc1;

uint32_t adc_value = 0;
uint8_t current_mode = 1; // Mac dinh khoi dong o MODE 1 - AUTO
char msg[100];

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART1_UART_Init(void);
static void MX_ADC1_Init(void);
void Check_Button_And_Input(void);
void Process_LED_Mode(void);

/* HAL compatible functions for UART & ADC */
HAL_StatusTypeDef HAL_UART_Transmit(UART_HandleTypeDef *huart, uint8_t *pData, uint16_t Size, uint32_t Timeout)
{
  for (uint16_t i = 0; i < Size; i++)
  {
    uint32_t t = 50000;
    while (!(huart->Instance->SR & USART_SR_TXE) && --t);
    huart->Instance->DR = pData[i];
  }
  uint32_t t = 50000;
  while (!(huart->Instance->SR & USART_SR_TC) && --t);
  return HAL_OK;
}

HAL_StatusTypeDef HAL_ADC_Start(ADC_HandleTypeDef *hadc)
{
  hadc->Instance->CR2 |= (7 << 17); // EXTSEL = SWSTART
  hadc->Instance->CR2 |= ADC_CR2_EXTTRIG;
  hadc->Instance->CR2 |= ADC_CR2_SWSTART;
  hadc->Instance->CR2 |= ADC_CR2_ADON;
  return HAL_OK;
}

HAL_StatusTypeDef HAL_ADC_PollForConversion(ADC_HandleTypeDef *hadc, uint32_t Timeout)
{
  uint32_t t = 50000;
  while (!(hadc->Instance->SR & ADC_SR_EOC) && --t);
  return HAL_OK;
}

uint32_t HAL_ADC_GetValue(ADC_HandleTypeDef *hadc)
{
  return (uint32_t)(hadc->Instance->DR & 0x0FFF);
}

HAL_StatusTypeDef HAL_ADC_Stop(ADC_HandleTypeDef *hadc)
{
  return HAL_OK;
}

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* MCU Configuration--------------------------------------------------------*/
  HAL_Init();
  SystemClock_Config();
  SystemCoreClockUpdate();
  MX_GPIO_Init();
  MX_USART1_UART_Init();
  MX_ADC1_Init();

  /* Banner thong tin he thong */
  strcpy(msg, "\r\n=== HE THONG DIEU KHIEN LED ===\r\n");
  HAL_UART_Transmit(&huart1, (uint8_t *)msg, strlen(msg), HAL_MAX_DELAY);
  HAL_Delay(100);

  /* Infinite loop */
  while (1)
  {
    /* 1. Doc gia tri ADC tu cam bien LDR tren PA1 */
    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, HAL_MAX_DELAY);
    adc_value = HAL_ADC_GetValue(&hadc1);
    HAL_ADC_Stop(&hadc1);

    /* 2. Kiem tra nut nhan PA0 hoac ky tu gui tu Terminal de doi che do */
    Check_Button_And_Input();

    /* 3. Xu ly trang thai LED va tao chuoi thong bao theo Che do */
    Process_LED_Mode();

    /* 4. Gui thong bao qua USART1 len Virtual Terminal */
    HAL_UART_Transmit(&huart1, (uint8_t *)msg, strlen(msg), HAL_MAX_DELAY);

    /* Delay 400ms giua cac lan gui va kiem tra nut */
    for (int i = 0; i < 4; i++)
    {
      Check_Button_And_Input();
      HAL_Delay(100);
    }
  }
}

/**
  * @brief Kiem tra nut nhan PA0 va phim bam tu Virtual Terminal
  */
void Check_Button_And_Input(void)
{
  uint8_t mode_changed = 0;

  /* Cach 1: Nut nhan vat ly tren chan PA0 (Active LOW) */
  if (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_0) == GPIO_PIN_RESET)
  {
    HAL_Delay(20); // Chong rung phim
    if (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_0) == GPIO_PIN_RESET)
    {
      current_mode = (current_mode + 1) % 3;
      mode_changed = 1;
      while (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_0) == GPIO_PIN_RESET); // Cho nha nut
    }
  }

  /* Cach 2: Nhan phim truc tiep tu cua so Virtual Terminal */
  if (USART1->SR & USART_SR_RXNE)
  {
    char key = (char)(USART1->DR & 0xFF);
    if (key == '0') { current_mode = 0; mode_changed = 1; }
    else if (key == '1') { current_mode = 1; mode_changed = 1; }
    else if (key == '2') { current_mode = 2; mode_changed = 1; }
    else if (key == ' ' || key == '\r' || key == '\n') {
      current_mode = (current_mode + 1) % 3;
      mode_changed = 1;
    }
  }

  /* Neu co doi Mode, thong bao ngay lap tuc len Terminal */
  if (mode_changed)
  {
    char alert[60];
    if (current_mode == 0)
      strcpy(alert, "\r\n>>> Doi Mode 0 - Den luon tat <<<\r\n");
    else if (current_mode == 1)
      strcpy(alert, "\r\n>>> Doi Mode 1 - Tu dong <<<\r\n");
    else
      strcpy(alert, "\r\n>>> Doi Mode 2 - Den luon sang <<<\r\n");
    HAL_UART_Transmit(&huart1, (uint8_t *)alert, strlen(alert), HAL_MAX_DELAY);
  }
}

/**
  * @brief Dieu khien den LED theo che do va dinh dang chuoi gui UART
  */
void Process_LED_Mode(void)
{
  /* Ghi chu mach dien (Anode noi POWER, Cathode noi PA2/PA3/PA4):
     - RESET (0V) -> LED SANG
     - SET (3.3V) -> LED TAT
     - D1 (PA2) : LED-PINK   (Sang)
     - D2 (PA3) : LED-YELLOW (Binh thuong)
     - D3 (PA4) : LED-RED    (Toi)
  */

  if (current_mode == 0) // MODE 0: Den luon tat
  {
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2 | GPIO_PIN_3 | GPIO_PIN_4, GPIO_PIN_SET);
    sprintf(msg, "ADC = %4lu | Mode 0 - Den luon tat\r\n", adc_value);
  }
  else if (current_mode == 1) // MODE 1: Tu dong theo LDR (nguong lech 200 de de demo)
  {
    if (adc_value < 2850)
    {
      /* Sang -> D1 (Led hong tren PA2) SANG, Vang va Do TAT */
      HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2, GPIO_PIN_RESET);
      HAL_GPIO_WritePin(GPIOA, GPIO_PIN_3 | GPIO_PIN_4, GPIO_PIN_SET);
      sprintf(msg, "ADC = %4lu | Mode 1 - Sang - Led hong\r\n", adc_value);
    }
    else if (adc_value < 3050)
    {
      /* Binh thuong -> D2 (Led vang tren PA3) SANG, Hong va Do TAT */
      HAL_GPIO_WritePin(GPIOA, GPIO_PIN_3, GPIO_PIN_RESET);
      HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2 | GPIO_PIN_4, GPIO_PIN_SET);
      sprintf(msg, "ADC = %4lu | Mode 1 - Binh thuong - Led vang\r\n", adc_value);
    }
    else
    {
      /* Toi -> D3 (Led do tren PA4) SANG, Hong va Vang TAT */
      HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET);
      HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2 | GPIO_PIN_3, GPIO_PIN_SET);
      sprintf(msg, "ADC = %4lu | Mode 1 - Toi - Led do\r\n", adc_value);
    }
  }
  else // MODE 2: Den luon sang
  {
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2 | GPIO_PIN_3 | GPIO_PIN_4, GPIO_PIN_RESET);
    sprintf(msg, "ADC = %4lu | Mode 2 - Den luon sang\r\n", adc_value);
  }
}

/**
  * @brief System Clock Configuration (HSI 8MHz)
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief USART1 Initialization Function (9600 bps, 8N1)
  *        PA9: TX, PA10: RX
  */
static void MX_USART1_UART_Init(void)
{
  __HAL_RCC_GPIOA_CLK_ENABLE();
  RCC->APB2ENR |= RCC_APB2ENR_USART1EN;

  /* PA9 (TX) -> Alternate Function Output Push-Pull */
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  GPIO_InitStruct.Pin = GPIO_PIN_9;
  GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /* PA10 (RX) -> Input Floating */
  GPIO_InitStruct.Pin = GPIO_PIN_10;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /* Tinh toan BRR cho baud rate 9600 bps tren Proteus */
  #ifdef USE_8MHZ
    USART1->BRR = 833;  // 8MHz / 9600
  #else
    USART1->BRR = 7500; // 72MHz / 9600 (mac dinh Proteus la 72M)
  #endif

  USART1->CR1 = USART_CR1_UE | USART_CR1_TE | USART_CR1_RE;

  huart1.Instance = USART1;
}

/**
  * @brief ADC1 Initialization Function (PA1 noi voi cam bien LDR)
  */
static void MX_ADC1_Init(void)
{
  __HAL_RCC_GPIOA_CLK_ENABLE();
  RCC->APB2ENR |= RCC_APB2ENR_ADC1EN;

  /* PA1 -> Analog Input */
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  GPIO_InitStruct.Pin = GPIO_PIN_1;
  GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /* Chia tan so ADC (PCLK2 / 6) */
  RCC->CFGR &= ~RCC_CFGR_ADCPRE;
  RCC->CFGR |= RCC_CFGR_ADCPRE_DIV6;

  /* Cau hinh ADC1 */
  ADC1->CR1 = 0;
  ADC1->CR2 = ADC_CR2_ADON;
  ADC1->SQR1 = 0;          // 1 conversion
  ADC1->SQR3 = 1;          // Kenh 1 (PA1)
  ADC1->SMPR2 = (7 << 3);  // 239.5 cycles cho Kenh 1

  hadc1.Instance = ADC1;
}

/**
  * @brief GPIO Initialization Function:
  *        - PA0: Nut nhan Input Pull-Up
  *        - PA2, PA3, PA4: Cac den LED Output Push-Pull
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  __HAL_RCC_GPIOA_CLK_ENABLE();

  /* 1. Nut nhan tren chan PA0 (Input Pull-up) */
  GPIO_InitStruct.Pin = GPIO_PIN_0;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /* 2. Cac den LED tren PA2, PA3, PA4 (Output Push-Pull) */
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_2 | GPIO_PIN_3 | GPIO_PIN_4, GPIO_PIN_SET); // Ban dau tat
  GPIO_InitStruct.Pin = GPIO_PIN_2 | GPIO_PIN_3 | GPIO_PIN_4;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
}

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  __disable_irq();
  while (1)
  {
  }
}



