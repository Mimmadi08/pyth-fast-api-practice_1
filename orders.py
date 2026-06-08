from fastapi import APIRouter, HTTPException, Depends
from typing import List
import oracledb
from database import get_connection
from schemas import (
    OrderSearchRequest,
    OrderHeaderResponse,
    SingleOrderUpdateRequest,
    MultiOrderUpdateRequest,
    OrderCreateRequest
)
from auth import verify_api_key

# APIRouter is like a mini FastAPI app for grouping routes
router = APIRouter()

@router.post("/orders/search", dependencies=[Depends(verify_api_key)], response_model=List[OrderHeaderResponse])
def search_orders(request: OrderSearchRequest, skip: int = 0, limit: int = 10):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Build WHERE clause dynamically
        conditions = []
        params = {}

        if request.division_id is not None:
            conditions.append("DIVISION_ID = :division_id")
            params["division_id"] = request.division_id

        if request.order_type is not None:
            conditions.append("ORDER_TYPE = :order_type")
            params["order_type"] = request.order_type

        if request.order_status is not None:
            conditions.append("ORDER_STATUS = :order_status")
            params["order_status"] = request.order_status

        if request.channel is not None:
            conditions.append("CHANNEL = :channel")
            params["channel"] = request.channel

        if request.store_num is not None:
            conditions.append("STORE_NUM = :store_num")
            params["store_num"] = request.store_num

        where_clause = " AND ".join(conditions)

        # ← must be indented at this level (8 spaces)
        sql = f"""
            SELECT *
            FROM (
                SELECT a.*, ROWNUM rnum
                FROM (
                    SELECT
                        ORDER_HEADER_ID,
                        ORDER_TYPE,
                        STORE_NUM,
                        ATTRINUTE2,
                        PROGRAM_TYPE,
                        TO_CHAR(REQUEST_DELIVERY_DATE, 'MM/DD/YYYY') AS REQUEST_DELIVERY_DATE,
                        ORDER_STATUS,
                        CUSTOMER_DEPT_NUM,
                        CSOR_CONFIRMATION_NUMBER
                    FROM OMS_ORD_DATA.OMS_PRE_ORDER_HEADERS
                    WHERE {where_clause}
                ) a
                WHERE ROWNUM <= :end_row
            )
            WHERE rnum > :start_row
        """

        params["end_row"] = skip + limit
        params["start_row"] = skip

        cursor.execute(sql, params)

        columns = [col[0].lower() for col in cursor.description]
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            raise HTTPException(status_code=404, detail="No orders found")

        return [dict(zip(columns, row)) for row in rows]

    except oracledb.DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")
    
# ── GET /orders/no-lines ────────────────────────────────
@router.get("/orders/no-lines", dependencies=[Depends(verify_api_key)])
def get_orders_no_lines(
    order_status: str = "U",
    order_type: str = "Regular"
):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT
                x.ORDER_HEADER_ID,
                x.ORDER_TYPE,
                x.STORE_NUM,
                x.ATTRINUTE2,
                x.PROGRAM_TYPE,
                TO_CHAR(x.REQUEST_DELIVERY_DATE, 'MM/DD/YYYY') AS REQUEST_DELIVERY_DATE,
                x.ORDER_STATUS,
                x.CUSTOMER_DEPT_NUM,
                x.CSOR_CONFIRMATION_NUMBER
            FROM OMS_ORD_DATA.OMS_PRE_ORDER_HEADERS x
            WHERE x.ORDER_STATUS = :order_status
              AND x.ORDER_TYPE   = :order_type
              AND x.ORDER_HEADER_ID NOT IN (
                    SELECT l.ORDER_HEADER_ID
                    FROM apps.oms_pre_order_lines l
                    WHERE l.ORDER_HEADER_ID = x.ORDER_HEADER_ID
              )
            ORDER BY x.CREATION_DATE
        """

        cursor.execute(sql, {
            "order_status": order_status,
            "order_type":   order_type
        })

        columns = [col[0].lower() for col in cursor.description]
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="No orders without lines found"
            )

        return [dict(zip(columns, row)) for row in rows]

    except oracledb.DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")
    
# ── POST /orders — Create new order ────────────────────
@router.post("/orders", dependencies=[Depends(verify_api_key)])
def create_order(request: OrderCreateRequest):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Get next sequence value for ORDER_HEADER_ID
        cursor.execute("SELECT OMS_ORD_DATA.OMS_PRE_ORDER_HEADERS_S.NEXTVAL FROM DUAL")
        new_id = cursor.fetchone()[0]

        sql = """
            INSERT INTO OMS_ORD_DATA.OMS_PRE_ORDER_HEADERS (
                ORDER_HEADER_ID,
                ORDER_TYPE,
                STORE_NUM,
                DIVISION_ID,
                CHANNEL,
                ORDER_STATUS,
                CUSTOMER_DEPT_NUM,
                REQUEST_DELIVERY_DATE,
                CUSTOMER_NOTES,
                DELIVERY_TYPE,
                CREATION_DATE,
                LAST_UPDATE_DATE
            ) VALUES (
                :order_header_id,
                :order_type,
                :store_num,
                :division_id,
                :channel,
                :order_status,
                :customer_dept_num,
                TO_DATE(:request_delivery_date, 'MM/DD/YYYY'),
                :customer_notes,
                :delivery_type,
                SYSDATE,
                SYSDATE
            )
        """

        cursor.execute(sql, {
            "order_header_id":      new_id,
            "order_type":           request.order_type,
            "store_num":            request.store_num,
            "division_id":          request.division_id,
            "channel":              request.channel,
            "order_status":         request.order_status,
            "customer_dept_num":    request.customer_dept_num,
            "request_delivery_date": request.request_delivery_date,
            "customer_notes":       request.customer_notes,
            "delivery_type":        request.delivery_type
        })

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "created": True,
            "order_header_id": new_id,
            "order_type": request.order_type,
            "store_num": request.store_num,
            "order_status": request.order_status
        }

    except oracledb.DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")

# ── GET /orders/{order_header_id} ──────────────────────
@router.get("/orders/{order_header_id}", dependencies=[Depends(verify_api_key)])
def get_order_by_id(order_header_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT
                ORDER_HEADER_ID,
                ORDER_TYPE,
                STORE_NUM,
                ATTRINUTE2,
                PROGRAM_TYPE,
                TO_CHAR(REQUEST_DELIVERY_DATE, 'MM/DD/YYYY') AS REQUEST_DELIVERY_DATE,
                ORDER_STATUS,
                CUSTOMER_DEPT_NUM,
                CSOR_CONFIRMATION_NUMBER
            FROM OMS_ORD_DATA.OMS_PRE_ORDER_HEADERS
            WHERE ORDER_HEADER_ID = :order_header_id
        """

        cursor.execute(sql, {"order_header_id": order_header_id})
        columns = [col[0].lower() for col in cursor.description]
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"Order {order_header_id} not found"
            )

        return dict(zip(columns, row))

    except oracledb.DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")

    # ── DELETE /orders/{order_header_id} ───────────────────
@router.delete("/orders/{order_header_id}", dependencies=[Depends(verify_api_key)])
def delete_order(order_header_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # First check if order exists
        cursor.execute(
            "SELECT ORDER_HEADER_ID FROM OMS_ORD_DATA.OMS_PRE_ORDER_HEADERS WHERE ORDER_HEADER_ID = :id",
            {"id": order_header_id}
        )
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Order {order_header_id} not found"
            )

        # Delete the order
        cursor.execute(
            "DELETE FROM OMS_ORD_DATA.OMS_PRE_ORDER_HEADERS WHERE ORDER_HEADER_ID = :id",
            {"id": order_header_id}
        )
        conn.commit()
        cursor.close()
        conn.close()

        return {"deleted": True, "order_header_id": order_header_id}

    except oracledb.DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")
    
    # ── PUT /orders/update/single ───────────────────────────
@router.put("/orders/update/single", dependencies=[Depends(verify_api_key)])
def update_single_order(request: SingleOrderUpdateRequest):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Check order exists
        cursor.execute(
            "SELECT ORDER_HEADER_ID FROM OMS_ORD_DATA.OMS_PRE_ORDER_HEADERS WHERE ORDER_HEADER_ID = :id",
            {"id": request.order_header_id}
        )
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Order {request.order_header_id} not found"
            )

        # Build dynamic SET clause
        updates = []
        params = {"order_header_id": request.order_header_id}

        if request.order_type is not None:
            updates.append("ORDER_TYPE = :order_type")
            params["order_type"] = request.order_type

        if request.order_status is not None:
            updates.append("ORDER_STATUS = :order_status")
            params["order_status"] = request.order_status

        if request.channel is not None:
            updates.append("CHANNEL = :channel")
            params["channel"] = request.channel

        if request.store_num is not None:
            updates.append("STORE_NUM = :store_num")
            params["store_num"] = request.store_num

        if request.request_delivery_date is not None:
            updates.append("REQUEST_DELIVERY_DATE = TO_DATE(:request_delivery_date, 'MM/DD/YYYY')")
            params["request_delivery_date"] = request.request_delivery_date

        if request.customer_notes is not None:
            updates.append("CUSTOMER_NOTES = :customer_notes")
            params["customer_notes"] = request.customer_notes

        if not updates:
            raise HTTPException(
                status_code=400,
                detail="No fields to update provided"
            )

        sql = f"""
            UPDATE OMS_ORD_DATA.OMS_PRE_ORDER_HEADERS
            SET {", ".join(updates)}
            WHERE ORDER_HEADER_ID = :order_header_id
        """

        cursor.execute(sql, params)
        conn.commit()
        cursor.close()
        conn.close()

        return {
            "updated": True,
            "order_header_id": request.order_header_id
        }

    except oracledb.DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")
    
    # ── PUT /orders/update/multi ────────────────────────────
@router.put("/orders/update/multi", dependencies=[Depends(verify_api_key)])
def update_multi_orders(request: MultiOrderUpdateRequest):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        updated = []
        not_found = []

        for order in request.orders:
            # Check each order exists
            cursor.execute(
                "SELECT ORDER_HEADER_ID FROM OMS_ORD_DATA.OMS_PRE_ORDER_HEADERS WHERE ORDER_HEADER_ID = :id",
                {"id": order.order_header_id}
            )
            if not cursor.fetchone():
                not_found.append(order.order_header_id)
                continue

            # Build dynamic SET clause
            updates = []
            params = {"order_header_id": order.order_header_id}

            if order.order_type is not None:
                updates.append("ORDER_TYPE = :order_type")
                params["order_type"] = order.order_type

            if order.order_status is not None:
                updates.append("ORDER_STATUS = :order_status")
                params["order_status"] = order.order_status

            if order.channel is not None:
                updates.append("CHANNEL = :channel")
                params["channel"] = order.channel

            if order.store_num is not None:
                updates.append("STORE_NUM = :store_num")
                params["store_num"] = order.store_num

            if order.request_delivery_date is not None:
                updates.append("REQUEST_DELIVERY_DATE = TO_DATE(:request_delivery_date, 'MM/DD/YYYY')")
                params["request_delivery_date"] = order.request_delivery_date

            if order.customer_notes is not None:
                updates.append("CUSTOMER_NOTES = :customer_notes")
                params["customer_notes"] = order.customer_notes

            if updates:
                sql = f"""
                    UPDATE OMS_ORD_DATA.OMS_PRE_ORDER_HEADERS
                    SET {", ".join(updates)}
                    WHERE ORDER_HEADER_ID = :order_header_id
                """
                cursor.execute(sql, params)
                updated.append(order.order_header_id)

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "updated": updated,
            "not_found": not_found,
            "total_updated": len(updated)
        }

    except oracledb.DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")