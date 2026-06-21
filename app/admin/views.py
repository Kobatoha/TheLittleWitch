from sqladmin import ModelView

from app.models import Category, Item, User
from app.models.plant import Plant
from app.models.garden_bed import GardenBed


class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"

    column_list = [User.id, User.username, User.email, User.is_active, User.created_at]
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [User.id, User.username, User.created_at]
    form_columns = [User.username, User.email, User.is_active]


class CategoryAdmin(ModelView, model=Category):
    name = "Категория"
    name_plural = "Категории"
    icon = "fa-solid fa-folder"

    column_list = [Category.id, Category.name, Category.description]
    column_searchable_list = [Category.name]
    form_columns = [Category.name, Category.description]


class ItemAdmin(ModelView, model=Item):
    name = "Товар"
    name_plural = "Товары"
    icon = "fa-solid fa-box"

    column_list = [
        Item.id,
        Item.name,
        Item.price,
        Item.category,
        Item.is_active,
    ]
    column_searchable_list = [Item.name]
    column_sortable_list = [Item.id, Item.name, Item.price]
    form_columns = [Item.name, Item.description, Item.price, Item.category, Item.is_active]

class PlantAdmin(ModelView, model=Plant):
    column_list = [Plant.id, Plant.name, Plant.growth_time, Plant.water_bonus, Plant.base_harvest_count]
    column_searchable_list = [Plant.name]
    column_sortable_list = [Plant.id, Plant.name, Plant.growth_time]
    form_columns = [Plant.name, Plant.growth_time, Plant.water_bonus, Plant.base_harvest_count, Plant.icon, Plant.description]
    name = "Растение"
    name_plural = "Растения"

class GardenBedAdmin(ModelView, model=GardenBed):
    column_list = [
        GardenBed.id, 
        GardenBed.player_id, 
        GardenBed.plant_id, 
        GardenBed.planted_at, 
        GardenBed.ready_at, 
        GardenBed.moisture,
    ]
    column_sortable_list = [
        GardenBed.id, 
        GardenBed.planted_at, 
        GardenBed.ready_at
    ]
    name = "Грядка"
    name_plural = "Грядки"

