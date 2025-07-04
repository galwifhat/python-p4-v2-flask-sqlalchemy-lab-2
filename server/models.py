from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin


metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Customer(db.Model, SerializerMixin):
    __tablename__ = "customers"

    serialize_rules = ("-reviews.customer",)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    reviews = db.relationship(
        "Review", back_populates="customer", cascade="all, delete-orphan"
    )

    # the `items` attribute on a Customer instance will represent a collection of Item objects.
    # The first argument, "reviews", is the name of the relationship on the Customer that leads to the association objects
    # (i.e., the collection of Review objects).
    # The second argument, "item", is the name of the attribute on the association object (Review)
    # that refers to the related object (Item).
    # The `creator` argument is a callable that defines how a new association object (Review) is created when we append an Item to the proxy.
    # The creator function takes the value that is being appended (which is an Item object) and returns a new Review instance.

    items = association_proxy(
        "reviews", "item", creator=lambda item_obj: Review(item=item_obj)
    )

    def __repr__(self):
        return f"<Customer {self.id}, {self.name}>"


class Item(db.Model, SerializerMixin):
    __tablename__ = "items"

    serialize_rules = ("-reviews.item",)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)

    reviews = db.relationship(
        "Review", back_populates="item", cascade="all, delete-orphan"
    )

    customers = association_proxy(
        "reviews",
        "customer",
        creator=lambda customer_obj: Review(customer=customer_obj),
    )

    def __repr__(self):
        return f"<Item {self.id}, {self.name}, {self.price}>"


class Review(db.Model, SerializerMixin):
    __tablename__ = "reviews"

    serialize_rules = ("-customer.reviews", "-item.reviews")

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)

    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))

    customer = db.relationship("Customer", back_populates="reviews")
    item = db.relationship("Item", back_populates="reviews")
