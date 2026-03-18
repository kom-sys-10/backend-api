from fastapi import APIRouter, Depends, Response
from services.productService import ProductService
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Annotated
from dependencies.productDependecies import get_product_service
from schemas.productSchema import CreateProductRequest

router = APIRouter(prefix="/api/product")
ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]

@router.get("/")
def get_all_products(productService: ProductServiceDep):
    products = productService.get_all_products()
    if not products:
        return Response(
            status_code = 204
        )
    return JSONResponse(
        content = jsonable_encoder(products),
        status_code = 200
    )

@router.get("/{pid}")
def get_product_by_id(pid: int, productService: ProductServiceDep):
    product = productService.get_product_by_id(pid)
    if not product:
        return Response(
            status_code = 204
        )
    return JSONResponse(
        content = jsonable_encoder(product),
        status_code = 200
    )

@router.post("/")
def create_product(body: CreateProductRequest, productService: ProductServiceDep):
    product = productService.create_product(body.name, body.price)
    if not product:
        return JSONResponse(
            content = jsonable_encoder({"msg": "Failed creating products"}),
            status_code = 400
        )
    return JSONResponse(
        content = jsonable_encoder(product),
        status_code = 200
    )
