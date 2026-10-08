cmake_minimum_required (VERSION 3.5)
project (pbrAudio LANGUAGES C CXX VERSION 0.3.4)
set (CMAKE_CXX_STANDARD 14)

if (NOT CMAKE_BUILD_TYPE)
  set (CMAKE_BUILD_TYPE "Release" CACHE STRING "Build type: Release or Debug" FORCE)
endif ()

# Define a persistent download directory (outside build directory)
set(EXTERNAL_DOWNLOAD_DIR "${CMAKE_SOURCE_DIR}/downloads" CACHE PATH "Directory for downloaded external files")

include(ExternalProject)
ExternalProject_Add(
    dill
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/1e/77/dc8c558f7593132cf8fefec57c4f60c83b16941c574ac5f619abb3ae7933/dill-0.4.1-py3-none-any.whl
    URL_HASH SHA256=1e1ce33e978ae97fcfcff5638477032b801c46c7c65cf717f95fbc2248f79a9d
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    pox
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/2a/ac/4d5f104edf2aae2fec85567ec1d1969010de8124c5c45514f25e14900b65/pox-0.3.7-py3-none-any.whl
    URL_HASH SHA256=82a495249d13371314c1a5b5626a115e067ef5215d49530bf5efa37fbc25b56a
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    klepto
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/7a/a1/ffa6a1502090e1e6a3893f2b8d2a8055abaf1f0b3ab7714acefb9e1d7bcd/klepto-0.2.8-py3-none-any.whl
    URL_HASH SHA256=61ff6c91966f6d114a5181f571f5757bfaab9d0ce20f61b0e73ffcab64167bec
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
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
ExternalProject_Add(
    networkx
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/9e/c9/b2622292ea83fbb4ec318f5b9ab867d0a28ab43c5717bb85b0a5f6b3b0a4/networkx-3.6.1-py3-none-any.whl
    URL_HASH SHA256=d47fbf302e7d9cbbb9e2555a0d267983d2aa476bac30e90dfbe5669bd57f3762
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
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
    URL    https://files.pythonhosted.org/packages/8f/f6/fb68b8c08f864ecee8f7f7ee2f1203ed5cba2335215de69e4f621eb47db5/trimesh-5.1.1-py3-none-any.whl
    URL_HASH SHA256=c5be85a3e31e9ff749f9b0aecc204e37a2cf7cca4e92cd066bb5f3d3c1127765
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
    URL    https://files.pythonhosted.org/packages/92/9d/c4e665119135114480843e7ab388fa94d8480650450e6f8e26b70d323a4c/urllib3-2.8.0-py3-none-any.whl
    URL_HASH SHA256=0cf3cae568d36aa9576b28dfb35f11328f1cb974ca7647d9475ebb86c75ac6e3
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
    URL    https://files.pythonhosted.org/packages/b5/70/5d8df3b09e25bce090399cf48e452d25c935ab72dad19406c77f4e828045/psutil-7.2.2-cp36-abi3-manylinux2010_x86_64.manylinux_2_12_x86_64.manylinux_2_28_x86_64.whl
    URL_HASH SHA256=076a2d2f923fd4821644f5ba89f059523da90dc9014e85f8e45a5774ca5bc6f9
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
    URL    https://files.pythonhosted.org/packages/09/7d/af933f0f6e0767995b4e2d705a0665e454d1c19402aa7e895de3951ebb04/scipy-1.17.1-cp311-cp311-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl
    URL_HASH SHA256=43af8d1f3bea642559019edfe64e9b11192a8978efbd1539d7bc2aaa23d92de4
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
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
    URL    https://files.pythonhosted.org/packages/b5/98/df615823cd9419131ce19fba00de53a663794369e198aade064a244b385d/zipp-4.1.1-py3-none-any.whl
    URL_HASH SHA256=8979f52d874162f485ff2981e3891f3a3317b7a3dd43ff1e1775b9304f307a9c
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
    URL    https://files.pythonhosted.org/packages/b3/55/ecca97ae19075f1fac62def77731e7f535e6c1fb8f92ff08160c5e6dade8/importlib_metadata-9.0.1-py3-none-any.whl
    URL_HASH SHA256=bba5600596a7e21f3eef53281cf28d6a5195634d2f2b78ff9501a3272c6eaab0
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
    URL    https://files.pythonhosted.org/packages/db/17/4c8beb6c8c4176c6bf143bfd7e1e4dd6719b00ced90738c7ac471b71c1df/toolz-1.2.0-py3-none-any.whl
    URL_HASH SHA256=890f820b1cb8152785aaf9386d8707770110809035800985ca65cb24ce1120ef
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
    URL    https://files.pythonhosted.org/packages/6c/c0/a98505f18594f1bce828bb159cec0fcf9860562f1a2c85913409fc8f3d9e/fsspec-2026.9.0-py3-none-any.whl
    URL_HASH SHA256=8dd6e646e99ea382bd85f97a45e6b526a442d79423a7dc673f1e2756d05fcb5f
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
    URL    https://files.pythonhosted.org/packages/88/39/799be3f2f0f38cc727ee3b4f1445fe6d5e4133064ec2e4115069418a5bb6/cloudpickle-3.1.2-py3-none-any.whl
    URL_HASH SHA256=9acb47f6afd73f60dc1df93bb801b472f05ff42fa6c84167d25cb206be1fbf4a
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
    URL    https://files.pythonhosted.org/packages/58/50/6c0d534c5f134586a8e1ba4e330569e32f057e33372ae556463212fb4cd3/click-8.5.0-py3-none-any.whl
    URL_HASH SHA256=255bc9599cf7748b4b1a446ccc735421bd08a2ae529a8b88597d3de5664ee360
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    donfig
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/0c/d5/c5db1ea3394c6e1732fb3286b3bd878b59507a8f77d32a2cebda7d7b7cd4/donfig-0.8.1.post1-py3-none-any.whl
    URL_HASH SHA256=2a3175ce74a06109ff9307d90a230f81215cbac9a751f4d1c6194644b8204f9d
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
    URL    https://files.pythonhosted.org/packages/f8/3a/4fc99e788bcfa1b3b3f21abf57da45898d807d007e7f6fd1c7300904eb70/dask-2026.8.0-py3-none-any.whl
    URL_HASH SHA256=ccc0c83a189b0398602435189771d28dad7b5773b6089bb8dce14ae732dd782c
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
    URL    https://files.pythonhosted.org/packages/33/dc/ba4eaf844972bf9647314079f3a4cad79f63614b388b667103a2e7f521df/numba-0.68.0-cp311-cp311-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl
    URL_HASH SHA256=68f92839637a2aaca8ae124c3abf91f648d2fade50953ea8e81ec604ac05a771
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
    URL    https://files.pythonhosted.org/packages/59/b2/a5234f59ccf69cc90d29c62e01cacd1d60403fc5dfac77b38e019237d301/llvmlite-0.50.0-cp311-cp311-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl
    URL_HASH SHA256=a6ffde00d4be8772a24e3e8b3af6bf86a79e7cf066d944ef56136b3957d707dc
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
    URL    https://files.pythonhosted.org/packages/7b/a2/70fd4432b924684c372df8b0a45708c36c057ef3596c9eb53e0a806b980b/soundfile-0.14.0-py2.py3-none-manylinux_2_28_x86_64.whl
    URL_HASH SHA256=1e38bac1853412871318e82a1ba69a8be677619b56025bbfcccdb41b6cafe82d
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
    URL    https://files.pythonhosted.org/packages/f7/a4/4399daaf8f7dfee9d7c3327fdb0426ee041cc63edc358b93911ceb2bfc7a/cffi-2.1.1-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
    URL_HASH SHA256=34e261f78cb6ceaaa36f42f2613f4380d94d9c759a9c73c769ee6e0247364632
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
    URL    https://files.pythonhosted.org/packages/82/3b/64d4899d73f91ba49a8c18a8ff3f0ea8f1c1d75481760df8c68ef5235bf5/rich-15.0.0-py3-none-any.whl
    URL_HASH SHA256=33bd4ef74232fb73fe9279a257718407f169c09b78a87ad3d296f548e27de0bb
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
    URL    https://files.pythonhosted.org/packages/43/3f/f88a53f60a472b46f4023f56d204dd7de33d34c5d2acbfa0d70a674e639e/threadpoolctl-3.7.0-py3-none-any.whl
    URL_HASH SHA256=cd8b60b5641b45c67bbf73c64c843235fc2d8a480c87389f52f5dbee893b86be
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
    URL    https://files.pythonhosted.org/packages/71/46/17f022dd3e953bf20a04a028a21ec746d942f8d2af30fa0f124fa0e6a684/pygments-2.21.0-py3-none-any.whl
    URL_HASH SHA256=2363c69b61c4a97c838da3b130dcd6468f4848992b21a82f2a63ec34377137d9
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
    URL    https://files.pythonhosted.org/packages/aa/83/800570e6a22376eb8d599920f70aead4779a63611696f567477c4e85a70f/msgpack-1.2.3-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl
    URL_HASH SHA256=382b219de3d436de3baba0f4b0c6d4336e8f5858d0eb047918b13b69a71c6c55
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
    URL    https://files.pythonhosted.org/packages/58/a2/bb081bab032533a855d44de1d56f8e8426114ff1ba5d1f07a438a0a654f8/idna-3.20-py3-none-any.whl
    URL_HASH SHA256=ab7ae7122974553370f0bdb919e1a960b2cd1bc1ef0276416d896db81c14582c
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
    URL    https://files.pythonhosted.org/packages/0b/a7/71ac2cff56fec219ed242bb11b8efb69fcc4bec75db06fb7bfe35de520e6/certifi-2026.7.22-py3-none-any.whl
    URL_HASH SHA256=62f22742b58a1a33014a2b6b706588a8d7e2a88ae7bd1a6ebe8c992928483775
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
    URL    https://files.pythonhosted.org/packages/99/91/8acff4f5e50511b911bbccb72b8628a49c68ce14148cd9f6431094859a90/annotated_types-0.8.0-py3-none-any.whl
    URL_HASH SHA256=f072f4d804ea359e4eaf198b1af7a8b0943881a87f31bb764f8bf219bb9419e0
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
    URL    https://files.pythonhosted.org/packages/67/81/4add07e5172b7ac40d8ed5ff580409a7801a4fe26d529bdd915401dabfbe/typing_inspection-0.4.4-py3-none-any.whl
    URL_HASH SHA256=65b8397ba37ccbce054456aaccddfc91e6e3083c92824df348d96ca832f3f147
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    pydantic_core
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/f0/14/7122b78e9915e7dd50f9dcec6041a4e32874907b41b9e0880db2f1c7ae1a/pydantic_core-2.50.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
    URL_HASH SHA256=ac223ea031905319a64d0df116979ae438b42d6265862a3d63c9f9808c2905a7
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
    URL    https://files.pythonhosted.org/packages/2d/eb/9146591cc819d040475bf7f2be786710c7f7eb8083693bf859728da2ca9c/pydantic-2.14.0-py3-none-any.whl
    URL_HASH SHA256=15fab1bea6f1dc5003b54fc2ecab230c1fd1dbade2acd4addc52d81e32416d4b
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
    URL    https://files.pythonhosted.org/packages/7e/22/e85faf23bd72a92d1921e37d674ca56eb298a3c8be31fdecef0ff2b3aaac/h2-4.4.1-py3-none-any.whl
    URL_HASH SHA256=0e25f1462b23c9cb82d9eb02e28bc706dac2a68cb457c6a0d74d63c8a2a5d0e6
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
    URL    https://files.pythonhosted.org/packages/12/b8/4bd346e22b28902df4d651910f5242c28d84e4a5c2435ca5c3f797ed7e2e/anyio-4.15.1-py3-none-any.whl
    URL_HASH SHA256=6152fdbbf9a77fdec97731721bebf7c4c44f7c29b424b0065826173efc7ed101
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
    numcodecs
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/54/4b/195ac84cc8f6077b4f0f421e8daee21b7f1bd88cb7716414234379fe68ec/numcodecs-0.16.5-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl
    URL_HASH SHA256=c398919ef2eb0e56b8e97456f622640bfd3deed06de3acc976989cbcb22628a3
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    pycparser
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/0c/c3/44f3fbbfa403ea2a7c779186dc20772604442dde72947e7d01069cbe98e3/pycparser-3.0-py3-none-any.whl
    URL_HASH SHA256=b727414169a36b7d524c1c3e31839a521725078d7b2ff038656844266160a992
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
    URL    https://files.pythonhosted.org/packages/ac/ed/26058d46a34c3afc95dbf46c47d4310274fff92e81388ba42f536c450d35/blosc2-4.14.1-cp311-abi3-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl
    URL_HASH SHA256=d5e65efe80740651c3b39a9fd98478f073c57bed51f7eebe1fdfe248dc259e37
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    yaml
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/71/60/917329f640924b18ff085ab889a11c763e0b573da888e8404ff486657602/pyyaml-6.0.3-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl
    URL_HASH SHA256=b8bb0864c5a28024fac8a632c443c87c5aa6f215c0b126c449ae1a150412f31d
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    packaging
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/63/34/ba1c580383c9eada3711951fef0795c80b829a078d72188184bcab9dd527/packaging-26.3-py3-none-any.whl
    URL_HASH SHA256=d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)
ExternalProject_Add(
    google_crc32c
    PREFIX "blender"
    URL    https://files.pythonhosted.org/packages/aa/e3/26685384e4b66ff0928d9566ef6110a7df76029175a1842329d7e3515f10/google_crc32c-1.9.0-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
    URL_HASH SHA256=86764b99e7a607830d93cb5b75e0ec3ff6cb06d3c274624418473cee701900d4
    BUILD_ALWAYS OFF
    DOWNLOAD_DIR "${EXTERNAL_DOWNLOAD_DIR}"
    DOWNLOAD_NO_EXTRACT ON
    DOWNLOAD_NO_PROGRESS ON
    BUILD_COMMAND cmake -E echo "Skipping build step."
    INSTALL_COMMAND cmake -E echo "Skipping install step."
    CONFIGURE_COMMAND cmake -E echo "Skipping configure step."
)

# Make a .zip-file which can be installed into Blender
if (NOT WIN32)
  add_custom_target (blender 
    DEPENDS dill
    DEPENDS pox
    DEPENDS klepto
    DEPENDS fast-simplification
    DEPENDS rtree
    DEPENDS python_fcl
    DEPENDS networkx
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
    DEPENDS locket
    DEPENDS partd
    DEPENDS zipp
    DEPENDS importlib_metadata
    DEPENDS toolz
    DEPENDS fsspec
    DEPENDS cloudpickle
    DEPENDS click
    DEPENDS donfig
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
    DEPENDS numexpr
    DEPENDS markdown-it-py
    DEPENDS httpcore
    DEPENDS h2
    DEPENDS anyio
    DEPENDS pydantic
    DEPENDS pydantic_core
    DEPENDS httpx
    DEPENDS blosc2
    DEPENDS pycparser
    DEPENDS numcodecs
    DEPENDS yaml
    DEPENDS packaging
    DEPENDS google_crc32c
)

add_dependencies(blender dill)
add_dependencies(blender pox)
add_dependencies(blender klepto)
add_dependencies(blender fast-simplification)
add_dependencies(blender rtree)
add_dependencies(blender python_fcl)
add_dependencies(blender networkx)
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
add_dependencies(blender locket)
add_dependencies(blender partd)
add_dependencies(blender zipp)
add_dependencies(blender importlib_metadata)
add_dependencies(blender toolz)
add_dependencies(blender fsspec)
add_dependencies(blender cloudpickle)
add_dependencies(blender donfig)
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
add_dependencies(blender packaging)
add_dependencies(blender google_crc32c)
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
add_dependencies(blender pydantic_core)
add_dependencies(blender numexpr)
add_dependencies(blender markdown-it-py)
add_dependencies(blender httpcore)
add_dependencies(blender h2)
add_dependencies(blender anyio)
add_dependencies(blender pydantic)
add_dependencies(blender httpx)
add_dependencies(blender blosc2)
add_dependencies(blender pycparser)
add_dependencies(blender numcodecs)
endif ()
