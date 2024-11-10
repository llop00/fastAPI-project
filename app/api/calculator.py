from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Union
from app.dependencies import verify_token
from fastapi import Depends

router = APIRouter(prefix="/calculator", tags=["calculator"])

class CalculationRequest(BaseModel):
    operation: str
    num1: float
    num2: Optional[float] = None  # Optional for operations like square root
    
def perform_calculation(operation: str, num1: float, num2: Optional[float] = None) -> float:
    if operation == "add":
        return num1 + num2
    elif operation == "subtract":
        return num1 - num2
    elif operation == "multiply":
        return num1 * num2
    elif operation == "divide":
        if num2 == 0:
            raise HTTPException(status_code=400, detail="Cannot divide by zero")
        return num1 / num2
    elif operation == "power":
        return num1 ** num2
    elif operation == "square_root":
        if num1 < 0:
            raise HTTPException(status_code=400, detail="Cannot calculate square root of negative number")
        return num1 ** 0.5
    else:
        raise HTTPException(status_code=400, detail="Invalid operation")

@router.post("/calculate")
async def calculate(
    data: CalculationRequest,
    user=Depends(verify_token)
) -> dict[str, Union[str, float]]:
    """
    Perform basic mathematical calculations.
    Available operations: add, subtract, multiply, divide, power, square_root
    """
    try:
        result = perform_calculation(data.operation, data.num1, data.num2)
        return {
            "operation": data.operation,
            "result": result
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

@router.get("/operations")
async def list_operations(user=Depends(verify_token)) -> dict[str, list[str]]:
    """List all available calculator operations"""
    return {
        "available_operations": [
            "add",
            "subtract",
            "multiply",
            "divide",
            "power",
            "square_root"
        ]
    }