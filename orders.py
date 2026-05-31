from fastapi import APIRouter, HTTPException
from typing import List
import oracledb
from database import get_connection
from schemas import OrderSearchRequest, OrderHeaderResponse

# APIRouter is like a mini FastAPI app for grouping routes
router = APIRouter()

@router.post("/orders/search", response_model=List[OrderHeaderResponse])
def search_orders(request: OrderSearchRequest):
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

        # Join all conditions with AND
        where_clause = " AND ".join(conditions)

        sql = f"""
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
        """

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