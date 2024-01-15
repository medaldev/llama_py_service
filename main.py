from flask import Flask, request, jsonify
from llama_cpp import Llama
from conversation import Conversation
import uuid
from pprint import pprint

app = Flask(__name__)


@app.route('/chat', methods=['GET'])
def handle_messages():
    data = request.json

    conv_id = data.get("conversation_id")
    message = data.get("message")
    over = data.get("over")

    if not conv_id:
        conv = Conversation()
        conv_id = conv.id
        conversations[conv_id] = conv
    else:
        conv_id = uuid.UUID(conv_id)

    if conv_id not in conversations:
        return jsonify({"status": "error", "hint": f"There is no conversation with particular conversation_id = {conv_id}."})

    if over:
        del conversations[conv_id]
        return jsonify({"status": "ok"})

    if not message:
        return jsonify({"status": "error",
                        "hint": "Message is absent in request.",
                        "conversation_id": conv_id,
                        })

    conversations[conv_id].add_message(message)

    messages = conversations[conv_id].get_messages()
    res = llm.create_chat_completion(messages)["choices"][0]["message"]
    conversations[conv_id].add_message(res.copy())

    res["conversation_id"] = conv_id
    res["status"] = "ok"

    pprint(messages)

    return jsonify(res)


if __name__ == '__main__':
    model_path = '/home/amedvedev/fprojects/llama.cpp/models/7B/llama-2-7b-chat.Q3_K_M.gguf'

    llm = Llama(model_path=model_path)

    conversations = {}

    app.run(debug=True)
