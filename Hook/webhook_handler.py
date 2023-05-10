from fastapi import FastAPI, Request
from Database import database
from datetime import datetime
from Telegram.telegram_bot import send_message_to_user
from Finam.finam_api import CustomOrderClient  # Импортируйте ваш модуль здесь
import config

app = FastAPI()
finam_client = CustomOrderClient(token=config.FINAM_API_TOKEN, base_url=config.FINAM_API_BASE_URL)

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    unique_token = data.get('unique_token', None)
    security_board = data.get('security_board', None)
    current_price = float(data.get('current_price', None))

    if unique_token:
        signal = database.get_signal_by_token(unique_token)

        if signal:
            _, unique_token, instrument, take_profit, stop_loss, position_type, amount = signal
            position = data.get('position', 'UNKNOWN')
            # Создаем стоп лосс и тейк профит
            # Создаем ордер
            print (position_type)
            payload={
                    "clientId" : config.CLIENT_ID,
                    "securityBoard": security_board,
                    "securityCode": instrument,
                    "buySell": position_type,
                    "quantity": int(amount),
                    "property" : "PutInQueue",
                    "market": True
                }
            created_order = await finam_client.create_order(payload)

            created_stop_order = await finam_client.create_stop_order(
                client_id=config.CLIENT_ID,
                security_board=security_board, #TQBR
                security_code=instrument,
                order_type=position_type,
                current_price=current_price,
                stop_loss_percent=stop_loss,
                take_profit_percent=take_profit
            )
            message_text = (f"Получен хук:\n"
                            f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f"Инструмент: {instrument}\n"
                            f"Позиция: {position}\n"
                            f"Тейк-профит: {take_profit}%\n"
                            f"Стоп-лосс: {stop_loss}%\n"
                            f"Размер: {amount}")

            await send_message_to_user(message_text)
        else:
            print("Токен не найден в базе данных")

    return {"status": "ok"}
