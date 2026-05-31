from pydantic import BaseModel, model_validator
from typing import Optional

class OrderSearchRequest(BaseModel):
    division_id: Optional[int] = None
    order_type: Optional[str] = None
    order_status: Optional[str] = None
    channel: Optional[str] = None
    store_num: Optional[str] = None

    @model_validator(mode="after")
    def check_at_least_two_fields(self):
        # Count how many fields have values
        filled = [
            self.division_id,
            self.order_type,
            self.order_status,
            self.channel,
            self.store_num
        ]
        count = sum(1 for f in filled if f is not None)

        if count < 2:
            raise ValueError("At least 2 parameters must be provided")

        return self

# What goes OUT from the API
class OrderHeaderResponse(BaseModel):
    order_header_id: Optional[int]
    order_type: Optional[str]
    store_num: Optional[str]
    attrinute2: Optional[str]
    program_type: Optional[str]
    request_delivery_date: Optional[str]
    order_status: Optional[str]
    customer_dept_num: Optional[str]
    csor_confirmation_number: Optional[int]