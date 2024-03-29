from src.entities.config import Config, ConfigField

configs: list[Config] = [
    Config(
        name="customer",
        api_tags=["Customer Management"],
        fields=[
            ConfigField(name="customer_id", type=int, location="path"),
            ConfigField(name="name", type=str, location="body"),
            ConfigField(name="email", type=str, location="body"),
            ConfigField(name="phone_number", type=str, location="body"),
            ConfigField(name="loyalty_points", type=int, location="body"),
        ],
    ),
    Config(
        name="product",
        api_tags=["Product Catalog"],
        fields=[
            ConfigField(name="product_id", type=int, location="path"),
            ConfigField(name="name", type=str, location="body"),
            ConfigField(name="price", type=float, location="body"),
            ConfigField(name="category", type=str, location="body"),
            ConfigField(name="stock", type=int, location="body"),
        ],
    ),
    Config(
        name="order",
        api_tags=["Order Processing"],
        fields=[
            ConfigField(name="order_id", type=int, location="path"),
            ConfigField(name="customer_id", type=int, location="body"),
            ConfigField(name="date", type=str, location="body"),
            ConfigField(name="total_amount", type=float, location="body"),
            ConfigField(name="status", type=str, location="body"),
        ],
    ),
    Config(
        name="employee",
        api_tags=["Employee Management"],
        fields=[
            ConfigField(name="employee_id", type=int, location="path"),
            ConfigField(name="name", type=str, location="body"),
            ConfigField(name="position", type=str, location="body"),
            ConfigField(name="department", type=str, location="body"),
            ConfigField(name="salary", type=float, location="body"),
        ],
    ),
    Config(
        name="invoice",
        api_tags=["Billing"],
        fields=[
            ConfigField(name="invoice_id", type=int, location="path"),
            ConfigField(name="order_id", type=int, location="body"),
            ConfigField(name="issue_date", type=str, location="body"),
            ConfigField(name="amount_due", type=float, location="body"),
            ConfigField(name="payment_status", type=str, location="body"),
        ],
    )

]
