cmake_minimum_required (VERSION 3.5)
project (pbrAudio LANGUAGES C CXX VERSION 0.3.4)
set (CMAKE_CXX_STANDARD 14)

if (NOT CMAKE_BUILD_TYPE)
  set (CMAKE_BUILD_TYPE "Release" CACHE STRING "Build type: Release or Debug" FORCE)
endif ()

# Define a persistent download directory (outside build directory)
set(EXTERNAL_DOWNLOAD_DIR "${CMAKE_SOURCE_DIR}/downloads" CACHE PATH "Directory for downloaded external files")

include(ExternalProject)
#ExternalProject_Add(
#    meshlib
#    PREFIX "blender"
#    URL    https://files.pythonhosted.org/packages/bf/3f/493a62fabbc257c48e96d64f8179455bb072cf503d8df4aa2485b305bbb0/meshlib-3.0.9.196-py38.py39.py310.py311.py312.py313.py314-none-manylinux_2_28_x86_64.whl
#    URL_HASH SHA256=801dea8770fa646a232a7861c4ba29471f41dc08fcb6ba333372ff4c09ee500b
#    BUILD_ALWAYS OFF
#    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
#    DOWNLOAD_NO_EXTRACT ON
#    DOWNLOAD_NO_PROGRESS ON
#    BUILD_COMMAND cmake -E echo "Skipping build step."
#    INSTALL_COMMAND cmake -E echo "Skipping install step."
#    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
#)
#ExternalProject_Add(
#    embreex
#    PREFIX "blender"
#    URL    https://files.pythonhosted.org/packages/60/10/c66c023923ca038d3081bf62e6a92ddefbd780e5ce0b7d5383abf10dc30f/embreex-2.17.7.post7-cp311-cp311-manylinux2010_x86_64.manylinux_2_12_x86_64.manylinux_2_28_x86_64.whl
#    URL_HASH SHA256=c4775a4d01f357c7a29ed7843ec811d59c778149f5fd4fdca2f3f42dc6ff45b6
#    BUILD_ALWAYS OFF
#    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
#    DOWNLOAD_NO_EXTRACT ON
#    DOWNLOAD_NO_PROGRESS ON
#    BUILD_COMMAND cmake -E echo "Skipping build step."
#    INSTALL_COMMAND cmake -E echo "Skipping install step."
#    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
#)
#ExternalProject_Add(
#    numpy
#    PREFIX "blender"
#    URL    https://files.pythonhosted.org/packages/65/fb/2b23769462b34398d9326081fad5655198fcf18966fcb1f1e49db44fbf31/numpy-2.3.5-cp311-cp311-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl
#    URL_HASH SHA256=8cba086a43d54ca804ce711b2a940b16e452807acebe7852ff327f1ecd49b0d4
#    BUILD_ALWAYS OFF
#    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
#    DOWNLOAD_NO_EXTRACT ON
#    DOWNLOAD_NO_PROGRESS ON
#    BUILD_COMMAND cmake -E echo "Skipping build step."
#    INSTALL_COMMAND cmake -E echo "Skipping install step."
#    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
#)
ExternalProject_Add(
    fast-simplification
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/8c/44/ae0b556d62ed6a8c6f290435f4764fae9944f6857171b60613ab35f0f1a7/fast_simplification-0.1.13-cp311-abi3-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl
    URL_HASH SHA256=c694f0f0bbafbaf29acf7043de603b4c85259f2eae7b802d4946d47976e9959d
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
#ExternalProject_Add(
#    pillow
#    PREFIX "blender"
#    URL    https://files.pythonhosted.org/packages/41/1e/db9470f2d030b4995083044cd8738cdd1bf773106819f6d8ba12597d5352/pillow-12.0.0-cp311-cp311-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl
#    URL_HASH SHA256=bee2a6db3a7242ea309aa7ee8e2780726fed67ff4e5b40169f2c940e7eb09227
#    BUILD_ALWAYS OFF
#    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
#    DOWNLOAD_NO_EXTRACT ON
#    DOWNLOAD_NO_PROGRESS ON
#    BUILD_COMMAND cmake -E echo "Skipping build step."
#    INSTALL_COMMAND cmake -E echo "Skipping install step."
#    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
#)
ExternalProject_Add(
    rtree
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/d1/75/e5d44be90525cd28503e7f836d077ae6663ec0687a13ba7810b4114b3668/rtree-1.4.1-py3-none-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl
    URL_HASH SHA256=12de4578f1b3381a93a655846900be4e3d5f4cd5e306b8b00aa77c1121dc7e8c
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    python_fcl
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/c6/71/cfe8928d36463972a011afb127dfdf18f903dab4184f2cffdf818e592514/python_fcl-0.7.0.10-cp311-cp311-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl
    URL_HASH SHA256=f942fe9307287f9c4dd6288881883afe29c80730e670cd0ad83851d2d0e27fcd
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
#ExternalProject_Add(
#    networkx
#    PREFIX "blender"
#    URL    https://files.pythonhosted.org/packages/07/c7/d64168da60332c17d24c0d2f08bdf3987e8d1ae9d84b5bbd0eec2eb26a55/networkx-3.6-py3-none-any.whl
#    URL_HASH SHA256=cdb395b105806062473d3be36458d8f1459a4e4b98e236a66c3a48996e07684f
#    BUILD_ALWAYS OFF
#    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
#    DOWNLOAD_NO_EXTRACT ON
#    DOWNLOAD_NO_PROGRESS ON
#    BUILD_COMMAND cmake -E echo "Skipping build step."
#    INSTALL_COMMAND cmake -E echo "Skipping install step."
#    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
#)
#ExternalProject_Add(
#    pympler
#    PREFIX "blender"
#    URL    https://files.pythonhosted.org/packages/79/4f/a6a2e2b202d7fd97eadfe90979845b8706676b41cbd3b42ba75adf329d1f/Pympler-1.1-py3-none-any.whl
#    URL_HASH SHA256=5b223d6027d0619584116a0cbc28e8d2e378f7a79c1e5e024f9ff3b673c58506
#    BUILD_ALWAYS OFF
#    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
#    DOWNLOAD_NO_EXTRACT ON
#    DOWNLOAD_NO_PROGRESS ON
#    BUILD_COMMAND cmake -E echo "Skipping build step."
#    INSTALL_COMMAND cmake -E echo "Skipping install step."
#    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
#)
ExternalProject_Add(
    resampy
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/4d/b9/3b00ac340a1aab3389ebcc52c779914a44aadf7b0cb7a3bf053195735607/resampy-0.4.3-py3-none-any.whl
    URL_HASH SHA256=ad2ed64516b140a122d96704e32bc0f92b23f45419e8b8f478e5a05f83edcebd
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    trimesh
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/8e/bc/f36afd1ad03d09cd0d311be5951f2dd705a824f34dd871779d42c277d741/trimesh-4.8.3-py3-none-any.whl
    URL_HASH SHA256=f9f1622ecac5f3bed5b65d3a748bb536481f52cd4e4e120e0b637cabe6cf1542
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    MarkupSafe
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/30/ac/0273f6fcb5f42e314c6d8cd99effae6a5354604d461b8d392b5ec9530a54/markupsafe-3.0.3-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl
    URL_HASH SHA256=0bf2a864d67e76e5c9a34dc26ec616a66b9888e25e7b9460e1c76d3293bd9dbf
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    tblib
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/27/44/aa5c8b10b2cce7a053018e0d132bd58e27527a0243c4985383d5b6fd93e9/tblib-3.1.0-py3-none-any.whl
    URL_HASH SHA256=670bb4582578134b3d81a84afa1b016128b429f3d48e6cbbaecc9d15675e984e
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    sortedcontainers
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/32/46/9cb0e58b2deb7f82b84065f37f3bffeb12413f947f9388e4cac22c4621ce/sortedcontainers-2.4.0-py2.py3-none-any.whl
    URL_HASH SHA256=a163dcaede0f1c021485e957a39245190e74249897e2ae4b2aa38595db237ee0
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    zict
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/80/ab/11a76c1e2126084fde2639514f24e6111b789b0bfa4fc6264a8975c7e1f1/zict-3.0.0-py2.py3-none-any.whl
    URL_HASH SHA256=5796e36bd0e0cc8cf0fbc1ace6a68912611c1dbd74750a3f3026b9b9d6a327ae
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    urllib3
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/a7/c2/fe1e52489ae3122415c51f387e221dd0773709bad6c6cdaa599e8a2c5185/urllib3-2.5.0-py3-none-any.whl
    URL_HASH SHA256=e6b01673c0fa6a13e374b50871808eb3bf7046c4b125b216f6bf1cc604cff0dc
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    tornado
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/f9/41/fb15f06e33d7430ca89420283a8762a4e6b8025b800ea51796ab5e6d9559/tornado-6.5.2-cp39-abi3-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl
    URL_HASH SHA256=e792706668c87709709c18b353da1f7662317b563ff69f00bab83595940c7108
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    psutil
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/9d/de/04c8c61232f7244aa0a4b9a9fbd63a89d5aeaf94b2fc9d1d16e2faa5cbb0/psutil-7.1.0-cp36-abi3-manylinux_2_12_x86_64.manylinux2010_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl
    URL_HASH SHA256=8c70e113920d51e89f212dd7be06219a9b88014e63a4cec69b684c327bc474e3
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    jinja2
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/62/a1/3d680cbfd5f4b8f15abc1d571870c5fc3e594bb582bc3b64ea099db13e56/jinja2-3.1.6-py3-none-any.whl
    URL_HASH SHA256=85ece4451f492d0c13c5dd7c13a64681a86afae63a5f347908daf103ce6d2f67
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    distributed
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/10/76/486da90111ae15daf88a25e464e271575de4197c331cca4d41c9c5db8bf4/distributed-2025.9.1-py3-none-any.whl
    URL_HASH SHA256=9453a2216cb9c686be12ad66b9c8698df3c3917565367de5797993a5f83f30ba
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    scipy
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/1a/bc/a5c75095089b96ea72c1bd37a4497c24b581ec73db4ef58ebee142ad2d14/scipy-1.16.2-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
    URL_HASH SHA256=f5db5ba6188d698ba7abab982ad6973265b74bb40a1efe1821b58c87f73892b9
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
#ExternalProject_Add(
#    pywavelets
#    PREFIX "blender"
#    URL    https://files.pythonhosted.org/packages/d8/8c/f316a153f7f89d2753df8a7371d15d0faab87e709fe02715dbc297c79385/pywavelets-1.9.0-cp311-cp311-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl
#    URL_HASH SHA256=d76b7fa8fc500b09201d689b4f15bf5887e30ffbe2e1f338eb8470590eb4521a
#    BUILD_ALWAYS OFF
#    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
#    DOWNLOAD_NO_EXTRACT ON
#    DOWNLOAD_NO_PROGRESS ON
#    BUILD_COMMAND cmake -E echo "Skipping build step."
#    INSTALL_COMMAND cmake -E echo "Skipping install step."
#    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
#)
ExternalProject_Add(
    locket
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/db/bc/83e112abc66cd466c6b83f99118035867cecd41802f8d044638aa78a106e/locket-1.0.0-py2.py3-none-any.whl
    URL_HASH SHA256=b6c819a722f7b6bd955b80781788e4a66a55628b858d347536b7e81325a3a5e3
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    partd
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/71/e7/40fb618334dcdf7c5a316c0e7343c5cd82d3d866edc100d98e29bc945ecd/partd-1.4.2-py3-none-any.whl
    URL_HASH SHA256=978e4ac767ec4ba5b86c6eaa52e5a2a3bc748a2ca839e8cc798f1cc6ce6efb0f
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    zipp
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/2e/54/647ade08bf0db230bfea292f893923872fd20be6ac6f53b2b936ba839d75/zipp-3.23.0-py3-none-any.whl
    URL_HASH SHA256=071652d6115ed432f5ce1d34c336c0adfd6a884660d1e9712a256d3d3bd4b14e
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    importlib_metadata
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/20/b0/36bd937216ec521246249be3bf9855081de4c5e06a0c9b4219dbeda50373/importlib_metadata-8.7.0-py3-none-any.whl
    URL_HASH SHA256=e5dd1551894c77868a30651cef00984d50e1002d06942a7101d34870c5f02afd
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    toolz
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/03/98/eb27cc78ad3af8e302c9d8ff4977f5026676e130d28dd7578132a457170c/toolz-1.0.0-py3-none-any.whl
    URL_HASH SHA256=292c8f1c4e7516bf9086f8850935c799a874039c8bcf959d47b600e4c44a6236
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    fsspec
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/47/71/70db47e4f6ce3e5c37a607355f80da8860a33226be640226ac52cb05ef2e/fsspec-2025.9.0-py3-none-any.whl
    URL_HASH SHA256=530dc2a2af60a414a832059574df4a6e10cce927f6f4a78209390fe38955cfb7
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    cloudpickle
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/7e/e8/64c37fadfc2816a7701fa8a6ed8d87327c7d54eacfbfb6edab14a2f2be75/cloudpickle-3.1.1-py3-none-any.whl
    URL_HASH SHA256=c8c5a44295039331ee9dad40ba100a9c7297b6f988e50e87ccdf3765a668350e
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    click
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/db/d3/9dcc0f5797f070ec8edf30fbadfb200e71d9db6b84d211e3b2085a7589a0/click-8.3.0-py3-none-any.whl
    URL_HASH SHA256=9b9f285302c6e3064f4330c05f05b81945b2a39544279343e6e7c5f27a9baddc
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    dask
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/25/60/3fcd548bed6d25016933e4b2984c9b82e4c1e760380e03d4100b1b4726e0/dask-2025.9.1-py3-none-any.whl
    URL_HASH SHA256=2a8a7dc933caaea2f47745a65a6ec93d9e616e12aab53b4f03ee161d31939110
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    numba
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/0e/7d/403be3fecae33088027bc8a95dc80a2fda1e3beff3e0e5fc4374ada3afbe/numba-0.62.1-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
    URL_HASH SHA256=604059730c637c7885386521bb1b0ddcbc91fd56131a6dcc54163d6f1804c872
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    llvmlite
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/e6/95/a13362fe71d1e88bea9e3cc58a3337b3302a3e4af68391df10389f3b7f78/llvmlite-0.45.0-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
    URL_HASH SHA256=c6815d0d3f96de34491d3dc192e11e933e3448ceff0b58572a53f39795996e01
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    soundfile
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/57/5e/70bdd9579b35003a489fc850b5047beeda26328053ebadc1fb60f320f7db/soundfile-0.13.1-py2.py3-none-manylinux_2_28_x86_64.whl
    URL_HASH SHA256=03267c4e493315294834a0870f31dbb3b28a95561b80b134f0bd3cf2d5f0e618
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    cffi
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/d7/91/500d892b2bf36529a75b77958edfcd5ad8e2ce4064ce2ecfeab2125d72d1/cffi-2.0.0-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
    URL_HASH SHA256=8941aaadaf67246224cee8c3803777eed332a19d909b47e29c9842ef1e79ac26
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    rich
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/e3/30/3c4d035596d3cf444529e0b2953ad0466f6049528a879d27534700580395/rich-14.1.0-py3-none-any.whl
    URL_HASH SHA256=536f5f1785986d6dbdea3c75205c473f970777b4a0d6c6dd1b696aa05a3fa04f
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
#ExternalProject_Add(
#    zarrs
#    PREFIX "blender"
#    URL    https://files.pythonhosted.org/packages/c5/fa/471e2511b0c77419ac2228ce72770e94e994ab99c6b9275cb3de1dcead2d/zarrs-0.2.3-cp311-abi3-manylinux_2_28_x86_64.whl
#    URL_HASH SHA256=ab4074056f01f3292c89cd769e8c0db92c0df076e3d36665eec7fc557a62a2ed
#    BUILD_ALWAYS OFF
#    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
#    DOWNLOAD_NO_EXTRACT ON
#    DOWNLOAD_NO_PROGRESS ON
#    BUILD_COMMAND cmake -E echo "Skipping build step."
#    INSTALL_COMMAND cmake -E echo "Skipping install step."
#    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
#)
#ExternalProject_Add(
#    zarr
#    PREFIX "blender"
#    URL    https://files.pythonhosted.org/packages/de/7c/ba8ca8cbe9dbef8e83a95fc208fed8e6686c98b4719aaa0aa7f3d31fe390/zarr-3.1.6-py3-none-any.whl
#    URL_HASH SHA256=b5a82c5079d1c3d4ee8f06746fa3b9a98a7d804300fa3f4be154362a33e1207e
#    BUILD_ALWAYS OFF
#    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
#    DOWNLOAD_NO_EXTRACT ON
#    DOWNLOAD_NO_PROGRESS ON
#    BUILD_COMMAND cmake -E echo "Skipping build step."
#    INSTALL_COMMAND cmake -E echo "Skipping install step."
#    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
#)
ExternalProject_Add(
    typing-extensions
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/49/d3/b8441a820a491ddfc024b0b0cf0393375b75ea13866d9c66727e54c2fc80/typing_extensions-4.16.0-py3-none-any.whl
    URL_HASH SHA256=481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    threadpoolctl
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/32/d5/f9a850d79b0851d1d4ef6456097579a9005b31fea68726a4ae5f2d82ddd9/threadpoolctl-3.6.0-py3-none-any.whl
    URL_HASH SHA256=43a0b8fd5a2928500110039e43a5eed8480b918967083ea48dc3ab9f13c4a7fb
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    pygments
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/f4/7e/a72dd26f3b0f4f2bf1dd8923c85f7ceb43172af56d63c7383eb62b332364/pygments-2.20.0-py3-none-any.whl
    URL_HASH SHA256=81a9e26dd42fd28a23a2d169d86d7ac03b46e2f8b59ed4698fb4785f946d0176
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    ndindex
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/fd/cb/7a02b6f29b15a16cd0002f4591d14493eff8e9236f7ca4c02ee4d4bcefbd/ndindex-1.10.1-cp311-cp311-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl
    URL_HASH SHA256=9fdf3ca16efcdfbb8800aa88fbab1bc6528e6a0504bcb9cf7af4cb9d50e9f5d9
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    msgpack
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/03/8d/671d81534ea0e2b0e8a121be100020da09eb78861fe3aa8f3ef7dcd3bed1/msgpack-1.2.1-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl
    URL_HASH SHA256=a28d076ca7c82b9c8728ad90b7147489449557038bed50e4241eb832395169b4
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    mdurl
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/b3/38/89ba8ad64ae25be8de66a6d463314cf1eb366222074cfda9ee839c56a4b4/mdurl-0.1.2-py3-none-any.whl
    URL_HASH SHA256=84008a41e51615a49fc9966191ff91509e3c40b939176e643fd50a5c2196b8f8
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    idna
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/1e/5e/d4e9f1a599fb8e573b7b87160658329fbf28d19eac2718f51fc3def3aa5a/idna-3.18-py3-none-any.whl
    URL_HASH SHA256=7f952cbe720b688055e3f87de14f5c3e5fdaa8bc3928985c4077ca689de849a2
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    hyperframe
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/48/30/47d0bf6072f7252e6521f3447ccfa40b421b6824517f82854703d0f5a98b/hyperframe-6.1.0-py3-none-any.whl
    URL_HASH SHA256=b03380493a519fce58ea5af42e4a42317bf9bd425596f7a0835ffce80f1a42e5
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    hpack
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/71/b4/4a9fcfb2aef6ba44d9073ecd301443aa00b3dac95de5619f2a7de7ec8a91/hpack-4.2.0-py3-none-any.whl
    URL_HASH SHA256=858ac0b02280fa582b5080d68db0899c62a80375e0e5413a74970c5e518b6986
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    h11
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/04/4b/29cac41a4d98d144bf5f6d33995617b185d14b22401f75ca86f384e87ff1/h11-0.16.0-py3-none-any.whl
    URL_HASH SHA256=63cf8bbe7522de3bf65932fda1d9c2772064ffb3dae62d55932da54b31cb6c86
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    certifi
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/ef/2f/c5464532e965badff2f4c4c1a3a83f5697f0d7c407ed0cda44aaa99bb451/certifi-2026.6.17-py3-none-any.whl
    URL_HASH SHA256=2227dcbaafe0d2f59279d1762ddddc37783ed4354594f194ffc31d20f41fc3db
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    annotated-types
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/78/b6/6307fbef88d9b5ee7421e68d78a9f162e0da4900bc5f5793f6d3d0e34fb8/annotated_types-0.7.0-py3-none-any.whl
    URL_HASH SHA256=1f02e8b43a8fbbc3f3e0d4f0f4bfc8131bcb4eebe8849b8e5c773f3a1c582a53
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    typing-inspection
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/dc/9b/47798a6c91d8bdb567fe2698fe81e0c6b7cb7ef4d13da4114b41d239f65d/typing_inspection-0.4.2-py3-none-any.whl
    URL_HASH SHA256=4ed1cacbdc298c220f1bd249ed5287caa16f34d44ef4e9c3d0cbad5b521545e7
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    pydantic-core
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/b6/4f/7fe179b37f887297a5bfd7b38a4a26cd485748b6b424c43c73a36c02f57b/pydantic_core-2.47.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
    URL_HASH SHA256=c9a891c20be5110deb1904f639f3615ec5022b3495995850d1abe7b8fa1550b5
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    numexpr
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/d6/15/9a7bf92b7c8047157fd96bc42ff6b0a20351f43aa58b9f61eb8f5ff3048b/numexpr-2.14.2-cp311-cp311-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl
    URL_HASH SHA256=f41170e9d0dbba76851e35d80cfa9f4ca5fe78628c5bf24d941cf3364940ab7a
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    markdown-it-py
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/b3/81/4da04ced5a082363ecfa159c010d200ecbd959ae410c10c0264a38cac0f5/markdown_it_py-4.2.0-py3-none-any.whl
    URL_HASH SHA256=9f7ebbcd14fe59494226453aed97c1070d83f8d24b6fc3a3bcf9a38092641c4a
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    httpcore
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/7e/f5/f66802a942d491edb555dd61e3a9961140fd64c90bce1eafd741609d334d/httpcore-1.0.9-py3-none-any.whl
    URL_HASH SHA256=2d400746a40668fc9dec9810239072b40b4484b640a8c38fd654a024c7a1bf55
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    h2
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/69/b2/119f6e6dcbd96f9069ce9a2665e0146588dc9f88f29549711853645e736a/h2-4.3.0-py3-none-any.whl
    URL_HASH SHA256=c438f029a25f7945c69e0ccf0fb951dc3f73a5f6412981daee861431b70e2bdd
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    anyio
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/da/35/f2287558c17e29fafc8ef3daf819bb9834061cfa43bff8014f7df7f63bdc/anyio-4.14.2-py3-none-any.whl
    URL_HASH SHA256=9f505dda5ac9f0c8309b5e8bd445a8c2bf7246f3ce950121e45ea15bc41d1494
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    pydantic
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/fd/7b/122376b1fd3c62c1ed9dc80c931ace4844b3c55407b6fb2d199377c9736f/pydantic-2.13.4-py3-none-any.whl
    URL_HASH SHA256=45a282cde31d808236fd7ea9d919b128653c8b38b393d1c4ab335c62924d9aba
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    httpx
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/2a/39/e50c7c3a983047577ee07d2a9e53faf5a69493943ec3f6a384bdc792deb2/httpx-0.28.1-py3-none-any.whl
    URL_HASH SHA256=d909fcccc110f8c7faf814ca82a9a4d816bc5a6dbfea25d6591d6985b8ba59ad
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    blosc2
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/ef/8d/f78ceadd7daee81e1ada2f393081823a623e698ad15bc3aefb971101b474/blosc2-4.9.1-cp311-cp311-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl
    URL_HASH SHA256=70ac9eb0eb82a33f2cec25759c2607bb6aa52dd32da6b6d0ec2a52315bedd4f1
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
#ExternalProject_Add(
#    donfig
#    PREFIX "blender"
#    URL    https://files.pythonhosted.org/packages/0c/d5/c5db1ea3394c6e1732fb3286b3bd878b59507a8f77d32a2cebda7d7b7cd4/donfig-0.8.1.post1-py3-none-any.whl
#    URL_HASH SHA256=2a3175ce74a06109ff9307d90a230f81215cbac9a751f4d1c6194644b8204f9d
#    BUILD_ALWAYS OFF
#    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
#    DOWNLOAD_NO_EXTRACT ON
#    DOWNLOAD_NO_PROGRESS ON
#    BUILD_COMMAND cmake -E echo "Skipping build step."
#    INSTALL_COMMAND cmake -E echo "Skipping install step."
#    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
#)
ExternalProject_Add(
    yaml
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/75/e4/2c27590dfc9992f73aabbeb9241ae20220bd9452df27483b6e56d3975cc5/PyYAML-6.0.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
    URL_HASH SHA256=3ad2a3decf9aaba3d29c8f537ac4b243e36bef957511b4766cb0057d32b0be85
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
#ExternalProject_Add(
#    numcodecs
#    PREFIX "blender"
#    URL    https://files.pythonhosted.org/packages/54/4b/195ac84cc8f6077b4f0f421e8daee21b7f1bd88cb7716414234379fe68ec/numcodecs-0.16.5-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl
#    URL_HASH SHA256=c398919ef2eb0e56b8e97456f622640bfd3deed06de3acc976989cbcb22628a3
#    BUILD_ALWAYS OFF
#    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
#    DOWNLOAD_NO_EXTRACT ON
#    DOWNLOAD_NO_PROGRESS ON
#    BUILD_COMMAND cmake -E echo "Skipping build step."
#    INSTALL_COMMAND cmake -E echo "Skipping install step."
#    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
#)
ExternalProject_Add(
    packaging
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/20/12/38679034af332785aac8774540895e234f4d07f7545804097de4b666afd8/packaging-25.0-py3-none-any.whl
    URL_HASH SHA256=29572ef2b1f17581046b3a2227d5c611fb25ec70ca1ba8554b24b0e69331a484
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
#ExternalProject_Add(
#    google-crc32c
#    PREFIX "blender"
#    URL    https://files.pythonhosted.org/packages/f6/fd/33aa4ec62b290477181c55bb1c9302c9698c58c0ce9a6ab4874abc8b0d60/google_crc32c-1.8.0-cp311-cp311-manylinux1_x86_64.manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_5_x86_64.whl
#    URL_HASH SHA256=19b40d637a54cb71e0829179f6cb41835f0fbd9e8eb60552152a8b52c36cbe15
#    BUILD_ALWAYS OFF
#    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
#    DOWNLOAD_NO_EXTRACT ON
#    DOWNLOAD_NO_PROGRESS ON
#    BUILD_COMMAND cmake -E echo "Skipping build step."
#    INSTALL_COMMAND cmake -E echo "Skipping install step."
#    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
#)
#ExternalProject_Add(
#    crc32c
#    PREFIX "blender"
#    URL    https://files.pythonhosted.org/packages/6a/2b/9e29e9ac4c4213d60491db09487125db358cd9263490fbadbd55e48fbe03/crc32c-2.7.1-cp311-cp311-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl
#    URL_HASH SHA256=d698eec444b18e296a104d0b9bb6c596c38bdcb79d24eba49604636e9d747305
#    BUILD_ALWAYS OFF
#    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
#    DOWNLOAD_NO_EXTRACT ON
#    DOWNLOAD_NO_PROGRESS ON
#    BUILD_COMMAND cmake -E echo "Skipping build step."
#    INSTALL_COMMAND cmake -E echo "Skipping install step."
#    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
#)
#ExternalProject_Get_property(zarr DOWNLOAD_DIR)

# Make a .zip-file which can be installed into Blender
if (NOT WIN32)
  add_custom_target (blender 
#    DEPENDS meshlib
#    DEPENDS embreex
#    DEPENDS numpy
    DEPENDS fast-simplification
#    DEPENDS pillow
    DEPENDS rtree
    DEPENDS python_fcl
#    DEPENDS networkx
#    DEPENDS pympler
    DEPENDS resampy
    DEPENDS trimesh
    DEPENDS MarkupSafe
    DEPENDS tblib
    DEPENDS sortedcontainers
    DEPENDS zict
    DEPENDS urllib3
    DEPENDS tornado
    DEPENDS psutil
    DEPENDS msgpack
    DEPENDS jinja2
    DEPENDS distributed
    DEPENDS scipy
#    DEPENDS pywavelets
    DEPENDS locket
    DEPENDS partd
    DEPENDS zipp
    DEPENDS importlib_metadata
    DEPENDS toolz
    DEPENDS fsspec
    DEPENDS cloudpickle
    DEPENDS click
    DEPENDS dask
    DEPENDS numba
    DEPENDS llvmlite
    DEPENDS soundfile
    DEPENDS cffi
    DEPENDS rich
#    DEPENDS zarrs
#    DEPENDS zarr
    DEPENDS typing-extensions
    DEPENDS threadpoolctl
    DEPENDS pygments
    DEPENDS ndindex
    DEPENDS msgpack
    DEPENDS mdurl
    DEPENDS idna
    DEPENDS hyperframe
    DEPENDS hpack
    DEPENDS h11
    DEPENDS certifi
    DEPENDS annotated-types
    DEPENDS typing-inspection
    DEPENDS pydantic-core
    DEPENDS numexpr
    DEPENDS markdown-it-py
    DEPENDS httpcore
    DEPENDS h2
    DEPENDS anyio
    DEPENDS pydantic
    DEPENDS httpx
    DEPENDS losc2
#    DEPENDS donfig
DEPENDS yaml
#    DEPENDS crc32c
#    DEPENDS google-crc32c
DEPENDS packaging
#    DEPENDS numcodecs
#    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio
#    COMMAND ${CMAKE_COMMAND} -E copy
#      "${CMAKE_CURRENT_SOURCE_DIR}/__init__.py"
#      pbrAudio
#    COMMAND ${CMAKE_COMMAND} -E copy
#      "${CMAKE_CURRENT_SOURCE_DIR}/blender_manifest.toml"
#      pbrAudio
#    COMMAND ${CMAKE_COMMAND} -E copy
#      "${CMAKE_CURRENT_SOURCE_DIR}/CREDITS"
#      pbrAudio
#    COMMAND ${CMAKE_COMMAND} -E copy
#      "${CMAKE_CURRENT_SOURCE_DIR}/LICENSE"
#      pbrAudio
#    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/engine
#    COMMAND ${CMAKE_COMMAND} -E copy_directory
#      "${CMAKE_CURRENT_SOURCE_DIR}/engine"
#      pbrAudio/engine
#    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/gui
#    COMMAND ${CMAKE_COMMAND} -E copy_directory
#      "${CMAKE_CURRENT_SOURCE_DIR}/gui"
#      pbrAudio/gui
#    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/properties
#    COMMAND ${CMAKE_COMMAND} -E copy_directory
#      "${CMAKE_CURRENT_SOURCE_DIR}/properties"
#      pbrAudio/properties
#    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/handlers
#    COMMAND ${CMAKE_COMMAND} -E copy_directory
#      "${CMAKE_CURRENT_SOURCE_DIR}/handlers"
#      pbrAudio/handlers
#    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/nodes
#    COMMAND ${CMAKE_COMMAND} -E copy_directory
#      "${CMAKE_CURRENT_SOURCE_DIR}/nodes"
#      pbrAudio/nodes
#    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/nodetrees
#    COMMAND ${CMAKE_COMMAND} -E copy_directory
#      "${CMAKE_CURRENT_SOURCE_DIR}/nodetrees"
#      pbrAudio/nodetrees
#    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/operators
#    COMMAND ${CMAKE_COMMAND} -E copy_directory
#      "${CMAKE_CURRENT_SOURCE_DIR}/operators"
#      pbrAudio/operators
#    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/sockets
#    COMMAND ${CMAKE_COMMAND} -E copy_directory
#      "${CMAKE_CURRENT_SOURCE_DIR}/sockets"
#      pbrAudio/sockets
#    COMMAND ${CMAKE_COMMAND} -E make_directory pbrAudio/wheels
#    COMMAND ${CMAKE_COMMAND} -E copy
#      "${DOWNLOAD_DIR}/*.whl"
#      pbrAudio/wheels
#    COMMAND ${CMAKE_COMMAND} -E copy
#      "${CMAKE_CURRENT_SOURCE_DIR}/wheels/*.whl"
#      pbrAudio/wheels
#    COMMAND ${CMAKE_COMMAND} -E tar "cfv" "${CMAKE_PROJECT_NAME}.zip" --format=zip pbrAudio
#    COMMAND ${CMAKE_COMMAND} -E remove_directory pbrAudio
)

#  add_dependencies(blender meshlib)
#  add_dependencies(blender embreex)
#  add_dependencies(blender numpy)
add_dependencies(blender fast-simplification)
#  add_dependencies(blender pillow)
add_dependencies(blender rtree)
add_dependencies(blender python_fcl)
#  add_dependencies(blender networkx)
#  add_dependencies(blender pympler)
add_dependencies(blender resampy)
add_dependencies(blender trimesh)
add_dependencies(blender MarkupSafe)
add_dependencies(blender tblib)
add_dependencies(blender sortedcontainers)
add_dependencies(blender zict)
add_dependencies(blender urllib3)
add_dependencies(blender tornado)
add_dependencies(blender psutil)
add_dependencies(blender msgpack)
add_dependencies(blender jinja2)
add_dependencies(blender distributed)
add_dependencies(blender scipy)
#  add_dependencies(blender pywavelets)
add_dependencies(blender locket)
add_dependencies(blender partd)
add_dependencies(blender zipp)
add_dependencies(blender importlib_metadata)
add_dependencies(blender toolz)
add_dependencies(blender fsspec)
add_dependencies(blender cloudpickle)
add_dependencies(blender click)
add_dependencies(blender dask)
add_dependencies(blender numba)
add_dependencies(blender llvmlite)
add_dependencies(blender soundfile)
add_dependencies(blender cffi)
add_dependencies(blender rich)
#  add_dependencies(blender zarrs)
#  add_dependencies(blender zarr)
add_dependencies(blender yaml)
#  add_dependencies(blender crc32c)
#  add_dependencies(blender google-crc32c)
add_dependencies(blender packaging)
#  add_dependencies(blender numcodecs)
#  add_dependencies(blender donfig)
add_dependencies(blender typing-extensions)
add_dependencies(blender threadpoolctl)
add_dependencies(blender pygments)
add_dependencies(blender ndindex)
add_dependencies(blender mdurl)
add_dependencies(blender idna)
add_dependencies(blender msgpack)
add_dependencies(blender hyperframe)
add_dependencies(blender hpack)
add_dependencies(blender h11)
add_dependencies(blender certifi)
add_dependencies(blender annotated-types)
add_dependencies(blender typing-inspection)
add_dependencies(blender pydantic-core)
add_dependencies(blender numexpr)
add_dependencies(blender markdown-it-py)
add_dependencies(blender httpcore)
add_dependencies(blender h2)
add_dependencies(blender anyio)
add_dependencies(blender pydantic)
add_dependencies(blender httpx)
add_dependencies(blender blosc2)
endif ()
