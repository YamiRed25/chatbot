const express = require('express');
const axios = require('axios');
const app = express();
const PORT = process.env.PORT || 5000;

// Middleware para processar JSON nas requisições POST
app.use(express.json());

// Seu token de verificação. Use o mesmo que está no painel da Meta.
const VERIFY_TOKEN = 'Tiago255';

// Seu token de acesso permanente que a aplicação usa para se autenticar.
const ACCESS_TOKEN = 'SEU_ACCESS_TOKEN_AQUI';

// O ID do seu WhatsApp Business.
const WHATSAPP_ID = "SEU_WHATSAPP_ID_AQUI";

// Rota para verificação de webhook (método GET)
app.get('/webhook', (req, res) => {
    const mode = req.query['hub.mode'];
    const token = req.query['hub.verify_token'];
    const challenge = req.query['hub.challenge'];

    if (mode && token) {
        if (mode === 'subscribe' && token === VERIFY_TOKEN) {
            console.log('Webhook verificado com sucesso!');
            res.status(200).send(challenge);
        } else {
            console.log('Falha na verificação do token.');
            res.sendStatus(403);
        }
    }
});

// Rota para receber mensagens (método POST)
app.post('/webhook', (req, res) => {
    const data = req.body;
    console.log('Dados recebidos:', JSON.stringify(data, null, 2));

    if (data.object === 'whatsapp_business_account') {
        data.entry.forEach(entry => {
            entry.changes.forEach(change => {
                if (change.value.messages) {
                    const message = change.value.messages[0];
                    const from_number = message.from;
                    const text_body = message.text.body;

                    console.log(`Mensagem recebida de ${from_number}: ${text_body}`);

                    // Lógica de resposta
                    if (text_body.toLowerCase() === 'olá') {
                        const response_text = "Olá! Eu sou seu assistente de teste da API da Meta.";
                        sendMessage(from_number, response_text);
                    } else {
                        const response_text = "Desculpe, não entendi. Tente 'Olá'.";
                        sendMessage(from_number, response_text);
                    }
                }
            });
        });
    }

    res.sendStatus(200);
});

// Função para enviar a mensagem
const sendMessage = (recipientId, messageBody) => {
    const url = `https://graph.facebook.com/v19.0/${WHATSAPP_ID}/messages`;
    
    const headers = {
        'Authorization': `Bearer ${ACCESS_TOKEN}`,
        'Content-Type': 'application/json'
    };

    const data = {
        "messaging_product": "whatsapp",
        "to": recipientId,
        "type": "text",
        "text": {
            "body": messageBody
        }
    };
    
    axios.post(url, data, { headers })
        .then(response => {
            console.log("Status da resposta da API:", response.status);
            console.log("Corpo da resposta:", JSON.stringify(response.data, null, 2));
        })
        .catch(error => {
            console.error("Erro ao enviar mensagem:", error.response?.status, error.response?.data);
        });
};

// Iniciar o servidor
app.listen(PORT, () => {
    console.log(`Servidor rodando na porta ${PORT}`);
});