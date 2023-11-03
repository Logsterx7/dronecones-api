import json

from flask import (
    Blueprint,
    request,
    session,
)

from api.db import get_db

bp = Blueprint("employee", __name__, url_prefix="/employee/<int:owner_id>")
# bp = Blueprint("employee", __name__, url_prefix="/employee")


@bp.route("/drones", methods=["GET"])
def drones(owner_id):
    # session.get("user_id")
    db = get_db()
    error = None
    query = """
    SELECT display_name, serial_number, is_active
    FROM drone
    WHERE owner_id = ?
    """
    drones = db.execute(query, (owner_id,)).fetchall()

    if drones is None:
        error = "This feature is not available yet - check back later!"
    elif len(drones) == 0:
        error = "No drones have been registered!"

    if error:
        return json.dumps({"error": error})
    else:
        # Convert the rows to a list of dictionaries
        drones_dict = [dict(drone) for drone in drones]

        # Return the JSON-serializable data
        return json.dumps({"drones": drones_dict})
    # return list of all drones and their immediately relevant info
    # response should look like: {'drones': [ {name: Drone2, size: number, id: 10394825, isActive: true } ]}


@bp.route("/earnings", methods=["GET"])
def earnings(owner_id):
    db = get_db()
    error = None
    # serial_number = body["display_name"]

    query = """
    SELECT id
    FROM drone
    WHERE owner_id = ?
    """
    drones = db.execute(query, (owner_id,)).fetchall()
    # drones_dict = {}
    if drones is None:
        error = "This feature is not available yet - check back later!"
    elif len(drones) == 0:
        error = "No drones have been registered!"
    else:
        employee_cut = 0
        for (
            drone
        ) in (
            drones
        ):  # change to have front in pass in a list of drones instead of looping through yourself.
            # print(drone["serial_number"])
            drone_id = drone["id"]
            query = """
            SELECT order_id
            FROM ordered_cone
            WHERE drone_id = ?
            """
            orders = db.execute(query, (drone_id,)).fetchall()
            if drones is None:
                error = "This feature is not available yet - check back later!"
            elif len(orders) == 0:
                error = "No orders have been submitted!"
            else:
                for order in orders:
                    # print(order["order_id"])
                    full_order_id = order["order_id"]
                    query = """
                    SELECT employee_cut
                    FROM full_order
                    WHERE id = ?
                    """
                    full_order = db.execute(query, (full_order_id,)).fetchall()
                    if drones is None:
                        error = "This feature is not available yet - check back later!"
                    elif len(full_order) == 0:
                        error = "full order table has not be set up correclty!"
                    else:
                        employee_cut += full_order["employee_cut"]

    if error:
        return json.dumps({"error": error})
    else:
        # Convert the rows to a list of dictionaries
        return json.dumps({"earnings": employee_cut})
        # return a single value with total earnings
        # example: {'earnings': 56600} for $566.00


@bp.route("/drone", methods=["POST", "DELETE", "PUT"])
def drone(owner_id):
    if request.method == "POST":
        body = request.get_json()

        display_name = body["display_name"]
        drone_size = body["drone_size"]
        serial_number = body["serial_number"]

        is_active = 1
        # session.get("user_id")
        db = get_db()
        error = None
        if not display_name:
            error = "Display Name is required."
        elif not drone_size:
            error = "Drone Size is required."
        # register a drone

        if error is None:
            try:
                query = """
                    INSERT INTO drone (serial_number, display_name, drone_size, owner_id, is_active)
                    VALUES (?, ?, ?, ?, ?)
                    """
                db.execute(
                    "INSERT INTO drone (serial_number, display_name, drone_size, owner_id, is_active) VALUES (?, ?, ?, ?, ?)",
                    (serial_number, display_name, drone_size, owner_id, is_active),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Drone {display_name} is already registered."
            else:
                return json.dumps({"success": display_name})
        # if we don't end up being able to register, return the error
        return json.dumps({"error": error})

    if request.method == "DELETE":
        db = get_db()
        error = None
        body = request.get_json()

        serial_number = body["serial_number"]

        if not serial_number:
            error = "Serial Number is required"

        if error is None:
            try:
                query = """
                    DELETE FROM drone
                    WHERE serial_number = ?
                    """
                db.execute(
                    "Delete From drone where serial_number = ?",  # will never fail because of how sql delete works
                    (serial_number),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Couldn't delete drone with serial {serial_number} because it does not exist."
            else:
                return json.dumps({"deleted drone with serial ": serial_number})
        return json.dumps({"error": error})

        # delete a drone's record

    if request.method == "PUT":
        db = get_db()
        serial_number = request.form["serial_number"]
        display_name = request.form["display_name"]
        is_active = request.form["is_active"]

        if not serial_number:
            error = "Serial Number is required"
        elif not display_name:
            error = "Display Name is required."
        elif not is_active:
            error = "Active State is required."

        try:
            query = """
                UPDATE drone
                SET display_name = ?, is_active = ? 
                WHERE serial_number = ?
                """
            db.execute(
                "UPDATE drone SET display_name = ?, is_active = ? WHERE serial_number = ?",
                (display_name, is_active, serial_number),
            )
            db.commit()
        except db.IntegrityError:
            error = f"Couldn't find drone with serial {serial_number} because it does not exist."
        else:
            return json.dumps({"Updated drone with serial ": serial_number})
        return json.dumps({"error": error})
        # update a drone's record - change info, deactivate