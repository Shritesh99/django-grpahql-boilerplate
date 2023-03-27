from django.contrib.auth import get_user_model

import graphene
import graphql_social_auth
from graphql_jwt.shortcuts import get_token
from graphql_jwt.shortcuts import create_refresh_token
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()

class SocialAuth(graphql_social_auth.SocialAuthJWT):
    refresh_token = graphene.String()

    @classmethod
    def resolve(cls, root, info, social, **kwargs):
        if social.user.refresh_tokens.count() >= 1:
            refresh_token = social.user.refresh_tokens.last()
        else:
            refresh_token = create_refresh_token(social.user)

        return cls(
            social=social,
            token=get_token(social.user),
            refresh_token=refresh_token
        )

class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, username, password, email):
        user = get_user_model()(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()

        return CreateUser(user=user)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    social_user = SocialAuth.Field()

class Query(graphene.ObjectType):
    me = graphene.Field(UserType)

    # @login_required
    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged!')
        return user