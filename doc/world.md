# agarnet.world

- [Cell](#cell)
  - [Cell.\_\_init\_\_(\*args, \*\*kwargs)](#cell__init__args-kwargs)
  - [Cell attributes](#cell-attributes)
    - [Cell.cid](#cellcid)
    - [Cell.color](#cellcolor)
    - [Cell.is_agitated](#cellis_agitated)
    - [Cell.is_ejected_mass](#cellis_ejected_mass)
    - [Cell.is_food](#cellis_food)
    - [Cell.is_virus](#cellis_virus)
    - [Cell.mass](#cellmass)
    - [Cell.name](#cellname)
    - [Cell.pos](#cellpos)
    - [Cell.size](#cellsize)
  - [Cell methods](#cell-methods)
    - [Cell.\_\_lt\_\_(other)](#cell__lt__other)
    - [Cell.same_player(other)](#cellsame_playerother)
    - [Cell.update(\*args, \*\*kwargs)](#cellupdateargs-kwargs)
- [World](#world)
  - [World attributes](#world-attributes)
    - [World.cells](#worldcells)
    - [World.leaderboard_groups](#worldleaderboard_groups)
    - [World.leaderboard_names](#worldleaderboard_names)
    - [World.top_left](#worldtop_left)
    - [World.bottom_right](#worldbottom_right)
    - [World.center](#worldcenter)
    - [World.size](#worldsize)
  - [World methods](#world-methods)
    - [World.\_\_eq\_\_(other)](#world__eq__other)
    - [World.create_cell(cid)](#worldcreate_cellcid)
    - [World.reset()](#worldreset)
- [Player](#player)
  - [Player attributes](#player-attributes)
    - [Player.center](#playercenter)
    - [Player.is_alive](#playeris_alive)
    - [Player.is_spectating](#playeris_spectating)
    - [Player.nick](#playernick)
    - [Player.own_cells](#playerown_cells)
    - [Player.own_ids](#playerown_ids)
    - [Player.scale](#playerscale)
    - [Player.total_mass](#playertotal_mass)
    - [Player.total_size](#playertotal_size)
    - [Player.visible_area](#playervisible_area)
    - [Player.world](#playerworld)
  - [Player methods](#player-methods)
    - [Player.cells_changed()](#playercells_changed)
    - [Player.reset()](#playerreset)

## Cell

### Cell.\_\_init\_\_(\*args, \*\*kwargs)
See [`Cell.update()`](#cellupdateargs-kwargs) for the arguments.


### Cell attributes

#### Cell.cid
Unique ID of the cell. Positive (non-zero).

#### Cell.color
Tuple of floats `(r, g, b)`, where each channel is between `0.0` and `1.0`.

#### Cell.is_agitated
Sent by server.

Unknown meaning. Open an issue if you know what it's for.

#### Cell.is_ejected_mass
`True` iff the cell has no name and its size is between 37 and 38.

#### Cell.is_food
`True` iff the cell has no name and its size is below 20.

#### Cell.is_virus
Sent by server.

Official client renders these cells with a spiked border.

#### Cell.mass
`mass = size * size / 100`

Do not confuse with [`size`](#cellsize).

#### Cell.name
String. Can be empty for player-controlled cells.

#### Cell.pos
`Vec` instance. Server sends integer coordinates.

#### Cell.size
The cell's radius. Do not confuse with [`mass`](#cellmass).


### Cell methods

#### Cell.\_\_lt\_\_(other)
Compares by `mass` and `cid` in this order.

#### Cell.same_player(other)
Compares `name` and `color`.

Returns `True` if both are owned by the same player.

#### Cell.update(\*args, \*\*kwargs)
Parameters:

- `cid=-1`
- `x=0`
- `y=0`
- `size=0`
- `name=''`
- `color=(1, 0, 1)`
- `is_virus=False`
- `is_agitated=False`

See the [attributes](#cell-attributes) above for their descriptions.


## World


### World attributes

#### World.cells
`defaultdict`, mapping cell IDs to their instances.

To override the default cell class, set its `default_factory`:
```python
my_world.cells.default_factory = MyCustomCellClass
```

#### World.leaderboard_groups
List of angles (`float`) for the pie chart in `teams` mode.

#### World.leaderboard_names
List of `(cid, name)` pairs, from top to bottom (1st to 10th).

The `cid`s seem to always be the lowest ID of that player.

The name can be an empty string. The official client then displays "An unnamed cell" instead.

#### World.top_left
`Vec` of the top left corner coordinates.

#### World.bottom_right
`Vec` of the bottom right corner coordinates.

#### World.center
`Vec` of the center of the world rectangle.

#### World.size
`Vec(width, height)`


### World methods

#### World.\_\_eq\_\_(other)
Compares two worlds by comparing their leaderboards.

#### World.create_cell(cid)
Creates a new cell in the world.

Override to use a custom cell class.

#### World.reset()
Clears the `cells` and leaderboards, and sets all corners to `Vec(0, 0)`.


## Player


### Player attributes

#### Player.center
The center of all controlled cells.

#### Player.is_alive
`True` iff `own_ids` is not empty.

#### Player.is_spectating
`not self.is_alive`

#### Player.nick
String.

#### Player.own_cells
All controlled cell instances.

Generated from `own_ids`, so use `list(player.own_cells)` or loop over it once.

#### Player.own_ids
All controlled cell IDs.

#### Player.scale
Calculated in [`cells_changed()`](#playercells_changed).

#### Player.total_mass
Combined mass of all controlled cells.

#### Player.total_size
Combined size of all controlled cells.

#### Player.visible_area
Calculated like in the official client.

Returns `(Vec(left, top), Vec(right, bottom))`.

#### Player.world
The world that the player's cells are in.


### Player methods

#### Player.cells_changed()
Calculates `total_size`, `total_mass`, `scale`, and `center`.

Has to be called when the controlled cells (`own_ids`) change.

#### Player.reset()
Clears `nick` and `own_ids`, sets `center` to `world.center`, and then calls [`cells_changed()`](#playercells_changed).
