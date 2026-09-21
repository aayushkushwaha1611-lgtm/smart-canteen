"""Seed the database with realistic demo data.

    python seed.py

Creates categories, food items, students, an admin, orders across every
status (with tokens + status history), notifications, activity logs and
settings. DEMO ACCOUNTS (development only):
    admin@canteen.edu    / Admin@123
    student@college.edu  / Student@123
"""
from datetime import datetime, timedelta

from app import create_app, db
from app.models import (
    ActivityLog,
    Category,
    FoodItem,
    Notification,
    Order,
    OrderItem,
    OrderStatus,
    OrderStatusHistory,
    Setting,
    User,
)
from app.services.notification_service import NotificationService
from app.services.settings_service import DEFAULTS
from app.services.token_service import TokenService
from config import get_config

app = create_app(get_config())

NOW = datetime.utcnow()

CATEGORIES = [
    ("Breakfast", "breakfast", "Start the day right — hot & fresh.", 1),
    ("Snacks", "snacks", "Quick bites between lectures.", 2),
    ("Main Course", "main-course", "Full meals that feel like home.", 3),
    ("Fast Food", "fast-food", "Crowd favourites, ready fast.", 4),
    ("Beverages", "beverages", "Hot chai to cold coffee.", 5),
    ("Desserts", "desserts", "Always leave room for dessert.", 6),
]

# (name, slug, category-slug, price, prep_min, stock, threshold, special, image, description)
FOODS = [
    ("Masala Dosa", "masala-dosa", "breakfast", 70, 12, 40, 8, True,
     "images/foods/masala-dosa.jpg",
     "Crispy rice crêpe stuffed with spiced potato, served with coconut chutney and sambar."),
    ("Kanda Poha", "kanda-poha", "breakfast", 35, 6, 50, 10, False,
     "images/foods/poha.jpg",
     "Flattened rice with onion, peanuts, lemon and sev — a Maharashtrian classic."),
    ("Aloo Paratha", "aloo-paratha", "breakfast", 45, 10, 35, 8, False,
     "images/foods/poha.jpg",
     "Stuffed wheat paratha with butter, curd and pickle on the side."),
    ("Vada Pav", "vada-pav", "snacks", 25, 5, 60, 12, True,
     "images/foods/vada-pav.jpg",
     "Mumbai's favourite — spiced potato fritter in soft pav with chutneys and fried chilli."),
    ("Samosa (2 pcs)", "samosa", "snacks", 20, 5, 4, 6, False,
     "images/foods/samosa.jpg",
     "Two golden crispy samosas with tangy tamarind chutney."),
    ("Veg Puff", "veg-puff", "snacks", 30, 6, 0, 6, False,
     "images/foods/samosa.jpg",
     "Flaky pastry puff loaded with spiced vegetables."),
    ("Veg Thali", "veg-thali", "main-course", 120, 15, 25, 5, True,
     "images/foods/veg-thali.jpg",
     "Dal, seasonal sabzi, rice, 2 rotis, salad and pickle — the full canteen thali."),
    ("Rajma Chawal", "rajma-chawal", "main-course", 90, 12, 30, 6, False,
     "images/foods/veg-thali.jpg",
     "Slow-cooked kidney-bean curry over steamed rice, with onion salad."),
    ("Paneer Butter Masala", "paneer-butter-masala", "main-course", 130, 14, 18, 5, True,
     "images/foods/paneer-butter-masala.jpg",
     "Cottage cheese in rich tomato-butter gravy with jeera rice."),
    ("Veg Burger", "veg-burger", "fast-food", 80, 8, 35, 8, False,
     "images/foods/veg-burger.jpg",
     "Crispy veg patty, lettuce, tomato and cheese in a toasted sesame bun."),
    ("French Fries", "french-fries", "fast-food", 60, 7, 45, 10, False,
     "images/foods/french-fries.jpg",
     "Golden salted fries with ketchup dip."),
    ("Grilled Sandwich", "grilled-sandwich", "fast-food", 70, 8, 28, 6, False,
     "images/foods/veg-burger.jpg",
     "Triple-layer grilled sandwich with veggies, cheese and green chutney."),
    ("Masala Chai", "masala-chai", "beverages", 15, 4, 80, 20, False,
     "images/foods/masala-chai.jpg",
     "Adrak-elaichi chai brewed fresh in the canteen kettle."),
    ("Cold Coffee", "cold-coffee", "beverages", 60, 6, 22, 6, True,
     None,
     "Blended iced coffee with milk, topped with cream."),
    ("Fresh Lime Soda", "fresh-lime-soda", "beverages", 30, 3, 40, 10, False,
     None,
     "Sweet, salty or mixed — your call. Freshly squeezed."),
    ("Gulab Jamun (2 pcs)", "gulab-jamun", "desserts", 40, 4, 3, 6, False,
     None,
     "Warm khoya dumplings soaked in cardamom sugar syrup."),
    ("Ice Cream Sundae", "ice-cream-sundae", "desserts", 70, 5, 20, 5, False,
     None,
     "Vanilla scoops with chocolate sauce and roasted nuts."),
    ("Chocolate Brownie", "chocolate-brownie", "desserts", 85, 6, 15, 4, False,
     None,
     "Warm fudge brownie with a scoop of vanilla ice cream."),
]

STATUS_PATH = [
    OrderStatus.ORDER_PLACED,
    OrderStatus.CONFIRMED,
    OrderStatus.PREPARING,
    OrderStatus.READY_FOR_PICKUP,
    OrderStatus.COMPLETED,
]


def make_user(full_name, email, roll, phone, password, role="student", active=True):
    user = User(
        full_name=full_name,
        email=email,
        roll_number=roll,
        phone=phone,
        role=role,
        is_active=active,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    return user


def make_order(user, lines, final_status, placed_at, notes=None, cancel_reason=None):
    """Create a historical order with items, token and full status history.

    `lines` is a list of (food, quantity). Stock is NOT deducted — seeded
    stock values are the current kitchen levels.
    """
    total = round(sum(float(f.price) * q for f, q in lines), 2)
    est = max(int(f.prep_time_minutes) for f, _ in lines)
    order = Order(
        order_number=f"ORD-TMP-{user.id}-{placed_at.timestamp():.0f}",
        user_id=user.id,
        status=final_status,
        total_amount=total,
        notes=notes,
        estimated_minutes=est,
        estimated_ready_at=placed_at + timedelta(minutes=est),
        created_at=placed_at,
        updated_at=placed_at,
    )
    db.session.add(order)
    db.session.flush()
    order.order_number = f"ORD-{placed_at:%Y%m%d}-{order.id:04d}"

    for food, qty in lines:
        db.session.add(
            OrderItem(
                order_id=order.id,
                food_item_id=food.id,
                food_name=food.name,
                price=float(food.price),
                quantity=qty,
                line_total=round(float(food.price) * qty, 2),
            )
        )

    token = TokenService.generate(order, token_date=placed_at.date())

    if final_status == OrderStatus.CANCELLED:
        path = [OrderStatus.ORDER_PLACED, OrderStatus.CANCELLED]
        order.cancelled_at = placed_at + timedelta(minutes=3)
        order.cancel_reason = cancel_reason or "Cancelled by student"
    else:
        path = STATUS_PATH[: STATUS_PATH.index(final_status) + 1]

    step = 0
    for status in path:
        step += 2
        db.session.add(
            OrderStatusHistory(
                order_id=order.id,
                status=status,
                changed_by=user.id if status == OrderStatus.ORDER_PLACED else None,
                created_at=placed_at + timedelta(minutes=step),
            )
        )

    db.session.flush()
    NotificationService.notify_new_order(order)
    if final_status != OrderStatus.ORDER_PLACED:
        NotificationService.notify_status_change(order, final_status)
    return order, token


def run():
    with app.app_context():
        print("→ Recreating schema…")
        db.drop_all()
        db.create_all()

        # ---- categories & food -------------------------------------------
        cat_map = {}
        for name, slug, desc, sort in CATEGORIES:
            category = Category(name=name, slug=slug, description=desc, sort_order=sort)
            db.session.add(category)
            cat_map[slug] = category
        db.session.flush()

        food_map = {}
        for (name, slug, cat_slug, price, prep, stock, thr, special,
             image, desc) in FOODS:
            food = FoodItem(
                name=name,
                slug=slug,
                description=desc,
                category_id=cat_map[cat_slug].id,
                price=price,
                prep_time_minutes=prep,
                stock_quantity=stock,
                low_stock_threshold=thr,
                is_available=stock > 0,
                is_active=True,
                is_special=special,
                image=image,
            )
            db.session.add(food)
            food_map[slug] = food
        db.session.flush()

        # ---- users --------------------------------------------------------
        admin = make_user("Canteen Admin", "admin@canteen.edu", "ADMIN-01", "9876500001",
                          "Admin@123", role="admin")
        priya = make_user("Priya Deshmukh", "student@college.edu", "TYCS-001", "9876543210",
                          "Student@123")
        aarav = make_user("Aarav Sharma", "aarav.sharma@college.edu", "TYCS-042", "9876543211",
                          "Student@123")
        sneha = make_user("Sneha Iyer", "sneha.iyer@college.edu", "TYCS-018", "9876543212",
                          "Student@123")
        rohan = make_user("Rohan Verma", "rohan.verma@college.edu", "TYCS-077", "9876543213",
                          "Student@123", active=False)
        meera = make_user("Meera Nair", "meera.nair@college.edu", "TYCS-055", "9876543214",
                          "Student@123")

        # ---- orders across days & statuses --------------------------------
        d = lambda days, mins=0: NOW - timedelta(days=days, minutes=mins)

        orders = []
        orders.append(make_order(
            priya,
            [(food_map["masala-dosa"], 1), (food_map["masala-chai"], 2)],
            OrderStatus.COMPLETED, d(2, 120), notes="Extra chutney please"))
        orders.append(make_order(
            aarav,
            [(food_map["veg-thali"], 1)],
            OrderStatus.COMPLETED, d(2, 40)))
        orders.append(make_order(
            sneha,
            [(food_map["vada-pav"], 2), (food_map["masala-chai"], 1)],
            OrderStatus.COMPLETED, d(1, 90), notes="Less spicy"))
        orders.append(make_order(
            priya,
            [(food_map["paneer-butter-masala"], 1), (food_map["cold-coffee"], 1)],
            OrderStatus.CANCELLED, d(1, 30), cancel_reason="Class got cancelled"))
        orders.append(make_order(
            meera,
            [(food_map["veg-burger"], 1), (food_map["french-fries"], 1)],
            OrderStatus.COMPLETED, d(0, 150)))
        orders.append(make_order(
            aarav,
            [(food_map["rajma-chawal"], 1), (food_map["fresh-lime-soda"], 1)],
            OrderStatus.READY_FOR_PICKUP, d(0, 45)))
        orders.append(make_order(
            sneha,
            [(food_map["grilled-sandwich"], 1), (food_map["cold-coffee"], 1)],
            OrderStatus.PREPARING, d(0, 25), notes="No onion"))
        orders.append(make_order(
            priya,
            [(food_map["samosa"], 1), (food_map["masala-chai"], 1)],
            OrderStatus.CONFIRMED, d(0, 12)))
        orders.append(make_order(
            meera,
            [(food_map["gulab-jamun"], 2), (food_map["ice-cream-sundae"], 1)],
            OrderStatus.ORDER_PLACED, d(0, 4), notes="Jamun warm please"))

        # active order for the demo student → shows on their dashboard
        orders.append(make_order(
            priya,
            [(food_map["veg-burger"], 1), (food_map["chocolate-brownie"], 1)],
            OrderStatus.PREPARING, d(0, 8), notes="Brownie with extra ice-cream"))

        # ---- notifications for the demo student ---------------------------
        NotificationService.send(
            priya, "Welcome to Smart Canteen! 🎉",
            "Your account is ready. Order now to get your daily digital token.",
            "account", link="/dashboard", commit=False)

        # ---- activity log --------------------------------------------------
        for user, action, detail, ago in [
            (admin, "login", "Admin signed in", 30),
            (priya, "order_placed", "ORD demo order placed", 20),
            (admin, "order_status", "Kitchen updated orders", 15),
            (None, "seed", "Database seeded with demo data", 1),
        ]:
            db.session.add(ActivityLog(
                user_id=user.id if user else None,
                action=action, entity_type="system", detail=detail,
                ip_address="127.0.0.1", created_at=NOW - timedelta(minutes=ago),
            ))

        # ---- settings ------------------------------------------------------
        for key, (value, label) in DEFAULTS.items():
            db.session.add(Setting(key=key, value=value, label=label))

        db.session.commit()

        # ---- summary -------------------------------------------------------
        print("✓ Seeded:")
        print(f"    categories : {Category.query.count()}")
        print(f"    food items : {FoodItem.query.count()}")
        print(f"    users      : {User.query.count()} (1 admin, {User.query.count() - 1} students)")
        print(f"    orders     : {Order.query.count()}")
        print(f"    tokens     : {__import__('app.models', fromlist=['Token']).Token.query.count()}")
        print(f"    notifications: {Notification.query.count()}")
        print()
        print("Demo accounts (development only):")
        print("    admin@canteen.edu   / Admin@123")
        print("    student@college.edu / Student@123")


if __name__ == "__main__":
    run()
