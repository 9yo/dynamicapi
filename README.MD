<p align="center">
    <img src="https://github.com/9yo/dynamicapi/blob/main/static/logo.png?raw=true" width="500" height="300">
</p>
<p align="center">
<img src="https://github.com/9yo/dynamicapi/actions/workflows/tests.yml/badge.svg" />
</p>
<p align="center">
<img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" />
<img src="https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white" />
<img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" />

</p>



---

### TLDR

- A versatile framework for building FastAPI applications with dynamic model generation.
- Easily define your data models and let the framework auto-generate corresponding CRUD API routes.
- Make use of async database operations for improved performance.
- Tailor to a wide range of applications from simple CRUD APIs to complex data management systems.

---

<p align="center">
  <img src="https://github.com/9yo/dynamicapi/blob/main/static/showcase.gif?raw=true" alt="animated" />
</p>

---

### Overview

This project is a robust and scalable FastAPI framework designed for efficient data management and API development. Leveraging the power of Python's async capabilities and SQLAlchemy for database interactions, this framework offers a versatile approach to creating APIs with dynamic model generation and flexible storage solutions.

### Key Features

- **Dynamic API Route Generation**: Automatically generates API routes based on configurable entities.
- **Modular Storage Management**: Integrates with PostgreSQL, ensuring efficient data storage and retrieval.
- **Type-Safe Operations**: Utilizes Pydantic for rigorous data validation and type checking.
- **Asynchronous Support**: Leverages Python's async features for non-blocking database operations.
- **Scalable Architecture**: Designed to accommodate growing data needs and additional functionalities.

### Use Cases

- **Rapid API Development**: Streamlines the process of creating and deploying APIs for data-intensive applications.
- **Customizable Data Models**: Tailor data models and API endpoints to specific business requirements.
- **Data Management**: Ideal for applications requiring robust database operations, including CRMs, e-commerce platforms, and content management systems.

### Getting Started

To get started with this framework:

1. **Installation**: Clone the repository and install dependencies using Poetry.
   ```bash
   git clone <repository-url>
   cd <repository-name>
   poetry install
   ```

2. **Configuration**: Set up your database credentials and other configurations in `examples/config.py`.

3. **Run the Application**:
   ```bash
   poetry run python examples/app.py
   ```

### Examples

**Defining a Configurable Entity**:

```python
# examples/config.py
from src.entities.config import Config, ConfigField

configs: list[Config] = [
    Config(
        name="Entity1",
        api_tags=["Entity1"],
        fields=[
            ConfigField(name="field_1", type=int, location="path"),
            # Add more fields as needed
        ],
    ),
]
```

**Starting the Server**:
Run the server with Uvicorn:

```bash
poetry run uvicorn examples.app:application --reload
```

---

### Contributing

We welcome contributions! Please read our contributing guidelines for instructions on how to submit pull requests.

### License

This project is licensed under [MIT License](LICENSE).

---

For more detailed information, refer to the [documentation](#). Happy coding!

---
