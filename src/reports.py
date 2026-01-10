        filtered_df['День недели'] = filtered_df['Дата операции'].dt.day_name()
        filtered_df['Номер дня недели'] = filtered_df['Дата операции'].dt.weekday
        
        # Предполагаем, что расходы - это отрицательные суммы
        if 'Сумма платежа' in filtered_df.columns:
            filtered_df['Сумма расходов'] = filtered_df['Сумма платежа'].abs()
            
            # Считаем средние траты по дням недели
            result = filtered_df.groupby(['Номер дня недели', 'День недели'])['Сумма расходов'].mean().reset_index()
            result = result.sort_values('Номер дня недели')
            
            # Переименовываем колонки
            result.columns = ['Номер дня', 'День недели', 'Средние траты']
            result['Средние траты'] = result['Средние траты'].round(2)
        else:
            result = pd.DataFrame()
        logger.info("Проанализированы траты по дням недели")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при анализе трат по дням недели: {e}")
        return pd.DataFrame()


@report_decorator()
def spending_by_workday(
    transactions: pd.DataFrame,
    date: Optional[str] = None
) -> pd.DataFrame:
    """
    Анализирует средние траты в рабочие и выходные дни.
    Args:
        transactions: DataFrame с транзакциями
        date: Дата отсчета (по умолчанию текущая)
        
    Returns:
        DataFrame со средними тратами по типам дней
    """
    try:
        # Определяем дату отсчета
        if date is None:
            reference_date = datetime.now()
        else:
            reference_date = datetime.strptime(date, "%Y-%m-%d")
        
        # Вычисляем дату 3 месяца назад
        three_months_ago = reference_date - timedelta(days=90)
        # Преобразуем даты
        if 'Дата операции' not in transactions.columns:
            raise ValueError("Колонка 'Дата операции' не найдена")
        
        transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'])
        
        # Фильтруем по дате
        mask = (
            (transactions['Дата операции'] >= three_months_ago) &
            (transactions['Дата операции'] <= reference_date)
        )
        
        filtered_df = transactions[mask].copy()
        
        if filtered_df.empty:
            logger.warning("Нет данных за последние 3 месяца")
            return pd.DataFrame()
        
        # Определяем рабочие дни (понедельник-пятница = 0-4)
        filtered_df['Рабочий день'] = filtered_df['Дата операции'].dt.weekday < 5
        # Предполагаем, что расходы - это отрицательные суммы
        if 'Сумма платежа' in filtered_df.columns:
            filtered_df['Сумма расходов'] = filtered_df['Сумма платежа'].abs()
            
            # Считаем средние траты по типам дней
            result = filtered_df.groupby('Рабочий день')['Сумма расходов'].mean().reset_index()
            
            # Преобразуем булевы значения в понятные строки
            result['Тип дня'] = result['Рабочий день'].apply(
                lambda x: 'Рабочий день' if x else 'Выходной день'
            )
            result['Средние траты'] = result['Сумма расходов'].round(2)
            result = result[['Тип дня', 'Средние траты']]
        else:
            result = pd.DataFrame()
        logger.info("Проанализированы траты по типам дней")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при анализе трат по типам дней: {e}")
        return pd.DataFrame()
