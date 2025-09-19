from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)


# Seu token de verificação. Use o mesmo que está no painel da Meta.
VERIFY_TOKEN = 'Tiago255'

# Seu token de acesso permanente que a aplicação usa para se autenticar.
ACCESS_TOKEN = 'EAAPW1f74zfYBPfkzNWTZAYHk2ZAufSTvAP8NDjO6pPl3oNnoSU0CzHesDOrKNBRk5oSKum3jsG8ESDDEOJvTWZBPgasWN1OncoAZAM20HsRCfGwbcknYGYhUyVEE1ApNFlV7ZAChiZARZBZCc845YEFZCjZAWEHvKZC2xxQwjm83ekWNxz3haGlcxzP34LCMiJyaYZC9uwZDZD'

# O ID do seu WhatsApp Business. Encontre no painel da Meta.
WHATSAPP_ID = "753844114486317"

# Função para enviar mensagens
def send_message(recipient_id, message_body):
    url = f"https://graph.facebook.com/v19.0/{WHATSAPP_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {
            "body": message_body
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    print("Status:", response.status_code)
    print("Resposta:", response.text)

# Rota para verificação do webhook
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token and mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verificado com sucesso!")
        return challenge, 200
    else:
        return "Falha na verificação do token.", 403

# Rota para receber mensagens
@app.route("/webhook", methods=["POST"])
def handle_message():
    data = request.get_json()
    print("Dados recebidos:", data)

    if data.get("object") == "whatsapp_business_account":
        try:
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    for message in value.get("messages", []):
                        from_number = message.get("from")
                        message_type = message.get("type")

                        if message_type == "text":
                            text_body = message["text"]["body"].lower()
                            print(f"Mensagem recebida de {from_number}: {text_body}")

                            # --- Fluxo do atendente da hamburgueria ---
                            if "menu" in text_body or "cardápio" in text_body:
                                resposta = (
                                    "🍔 *Cardápio Hamburgueria do Tiago* 🍔\n\n"
                                    "1️⃣ X-Burguer - R$ 15\n"
                                    "2️⃣ X-Salada - R$ 18\n"
                                    "3️⃣ X-Bacon - R$ 20\n"
                                    "4️⃣ Combo Duplo + Refri - R$ 28\n\n"
                                    "Digite o número da opção para pedir."
                                )
                                send_message(from_number, resposta)

                            elif text_body in ["1", "2", "3", "4"]:
                                opcoes = {
                                    "1": "X-Burguer 🍔",
                                    "2": "X-Salada 🥗🍔",
                                    "3": "X-Bacon 🥓🍔",
                                    "4": "Combo Duplo + Refri 🥤🍔🍔"
                                }
                                resposta = f"✅ Você escolheu *{opcoes[text_body]}*. Para confirmar o pedido, mande seu endereço."
                                send_message(from_number, resposta)

                            elif "obrigado" in text_body or "valeu" in text_body:
                                send_message(from_number, "😃 Nós que agradecemos! Seu pedido já está sendo preparado.")

                            else:
                                send_message(from_number, "Olá! Seja bem-vindo à Hamburgueria 🍔.\nMande *menu* para ver o cardápio.")

                        else:
                            send_message(from_number, "Recebi sua mensagem, mas só entendo texto por enquanto. 😊")

        except Exception as e:
            print("Erro ao processar mensagem:", e)

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)