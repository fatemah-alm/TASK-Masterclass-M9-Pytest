import graphene

from food.schemas import FoodMutation, FoodQuery


class Query(FoodQuery, graphene.ObjectType):
    greet = graphene.String(name=graphene.String(default_value="World"))

    def resolve_greet(root, info: graphene.ResolveInfo, name: str) -> str:
        return f"Hello, {name}!"


class Mutation(FoodMutation, graphene.ObjectType):
    pass


SCHEMA = graphene.Schema(query=Query, mutation=Mutation)
