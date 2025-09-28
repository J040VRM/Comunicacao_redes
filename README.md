<div align="center">

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:1D976C,100:93F9B9&height=200&section=header&text=Message%20API&fontSize=50&fontColor=fff&animation=twinkling&fontAlignY=40">

<p align="center">
  <i>💬 A simple RESTful API built with Swift (Vapor) for creating and managing messages, tested via Python TCP requests.</i>
</p>

<p align="center">
  <i>💬 Uma API RESTful simples construída em Swift (Vapor) para criação e gerenciamento de mensagens, testada via requisições TCP em Python.</i>
</p>

---

### 🌟 Features | Funcionalidades

<div align="center">

|  Feature  | Description | Descrição |
|:---------:|:------------|:----------|
| 📩 | Create, read, and manage messages | Criar, ler e gerenciar mensagens |
| 🧾 | DTO pattern for message transfer | Uso de DTO para transferência de dados |
| 🛠️ | Controller-based architecture | Arquitetura baseada em controllers |
| 🌐 | REST routes with Vapor | Rotas REST implementadas com Vapor |
| 🐍 | Python client for TCP requests | Cliente Python para testes de requisições TCP |
| 🚨 | Error handling and validation | Tratamento de erros e validação |
| 🔄 | Separation between model, DTO, and controller | Separação entre modelo, DTO e controller |

</div>

---

### 🖼️ Diagrams | Diagramas

- **Diagrama de Classes:**  
  <img width="1513" height="909" alt="image" src="https://github.com/user-attachments/assets/daa0c111-756b-40d3-a339-09f309b8d5a1" />


- **Diagrama de Sequência:**  
 <img width="946" height="1161" alt="image" src="https://github.com/user-attachments/assets/b95b7722-e08e-44ed-ae56-111ed0a74018" />


---

### 📦 Dependencies | Dependências

```bash
Swift 5.7+
Vapor 4
Fluent (para persistência)
Python 3.10+ (para cliente TCP de teste)
```

### ▶️ How to Run | Como Executar
```bash
# Run Swift Vapor API
swift run

# Run Python TCP client
python3 TCP_req.py
```
