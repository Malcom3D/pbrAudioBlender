# Copyright (C) 2025 Malcom3D <malcom3d.gpl@gmail.com>
#
# This file is part of pbrAudio.
#
# pbrAudio is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pbrAudio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pbrAudio.  If not, see <https://www.gnu.org/licenses/>.
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
import math
from bpy.types import PropertyGroup, CollectionProperty
from bpy.props import IntProperty, FloatProperty, StringProperty, EnumProperty, PointerProperty, BoolProperty

classes = []
backend = None

class PBRAudioBlosc2FilterItem(PropertyGroup):
    """Property group for a single blosc2 filter item"""
    filter_type: EnumProperty(
        name="Filter",
        description="Select a filter for the blosc2 codec",
        items=[
            ('NOFILTER', "NOFILTER", "Use NOFILTER codec for audio storage"),
            ('SHUFFLE', "SHUFFLE", "Use SHUFFLE codec for audio storage"),
            ('BITSHUFFLE', "BITSHUFFLE", "Use BITSHUFFLE codec for audio storage"),
            ('DELTA', "DELTA", "Use DELTA codec for audio storage"),
            ('TRUNC_PREC', "TRUNC_PREC", "Use TRUNC_PREC codec for audio storage"),
            ('NDCELL', "NDCELL", "Use NDCELL codec for audio storage"),
            ('NDMEAN', "NDMEAN", "Use NDMEAN codec for audio storage"),
            ('BYTEDELTA', "BYTEDELTA", "Use BYTEDELTA codec for audio storage"),
            ('INT_TRUNC', "INT_TRUNC", "Use INT_TRUNC codec for audio storage"),
        ],
        default='NOFILTER'
    )

classes.append(PBRAudioBlosc2FilterItem)

class PBRAudioStorageProperties(PropertyGroup):
    def storage_bakend_list(self, context):
        # placeholder for dynamic backend EnumProperty items
        global backend
        if backend is None:
            backend = [('blosc2','blosc2','Use blosc2 as storage backend'),('zarr','zarr','Use zarr as storage backend')]
        return backend

    backend: EnumProperty(
        name="Backend",
        description="Backend Type",
        items=storage_bakend_list,
        default=0
    )

    root_path: StringProperty( 
        name="Root path",
        description="Backend root path",
        subtype='FILE_PATH',
        default='storage',
        options={'PATH_SUPPORTS_BLEND_RELATIVE', 'ANIMATABLE'}
    )

    blosc2_codec: EnumProperty(
        name="Codec",
        description="Codec Type",
        items=[
            ('BLOSCLZ', "BLOSCLZ", "Use BLOSCLZ codec for audio storage"),
            ('LZ4', "LZ4", "Use LZ4 codec for audio storage"),
            ('LZ4HC', "LZ4HC", "Use LZ4HC codec for audio storage"),
            ('ZSTD', "ZSTD", "Use ZSTD codec for audio storage"),
            ('ZLIB', "ZLIB", "Use ZLIB codec for audio storage"),
            ('NDLZ', "NDLZ", "Use NDLZ codec for audio storage"),
            ('ZFP_ACC', "ZFP_ACC", "Use ZFP_ACC codec for audio storage"),
            ('ZFP_PREC', "ZFP_PREC", "Use ZFP_PREC codec for audio storage"),
            ('ZFP_RATE', "ZFP_RATE", "Use ZFP_RATE codec for audio storage"),
            ],
        default='LZ4'
    )

    blosc2_clevel: IntProperty(
        name="Compression level",
        description="The compression level from 0 (no compression) to 9 (maximum compression)",
        default=1,
        min=0,
        max=9
    )

    blosc2_cparams_threads: IntProperty(
        name="Compression threads",
        description="Number of compression threads",
        default=8,
        min=0
    )

    blosc2_dparams_threads: IntProperty(
        name="De-Compression threads",
        description="Number of de-compression threads",
        default=16,
        min=0
    )

    chunk_size_samples: IntProperty(
        name="Chunk size lenght",
        description="The lenght of the chunk size in samples",
        default=65536,
        min=1
    )

    zarr_store_kwargs: StringProperty( 
        name="Zarr store parameters",
        description="Zarr store parameters",
        default=''
    )

classes.append(PBRAudioStorageProperties)
