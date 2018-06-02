from collections import namedtuple

Spell = namedtuple(
    'Spell',
    [
        'name',
        'level',
        'school',
        'casting_time',
        'components',
        'effect',
        'duration',
        'saving_throw',
        'spell_resistance',
        'range',
        'short_description',
        'description'
    ]
)
