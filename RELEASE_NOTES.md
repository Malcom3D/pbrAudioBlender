# pbrAudioBlender
This release introduces a major overhaul of the `pbrAudioBlender` toolset, focusing on stability, performance, and expanded creative control for acoustic rendering.

**Key Highlights:**
*   **New Rendering Options:** You can now export audio in various formats, including Ambisonic, Surround, and Binaural (with HRTF) directly from your Blender scene.
*   **Improved Interface:** We have introduced a new Viewport Panel and specialized widgets, making it easier to visualize and control your acoustic nodes and data directly in the 3D workspace.
*   **Performance Boosts:** The storage engine has been completely rewritten to handle large data more efficiently using parallel processing and optimized compression, keeping your Blender session responsive.
*   **Enhanced Material Workflow:** We added preset acoustic materials and a new preview node system to hear your material changes in real-time.
*   **Stability Improvements:** We have squashed numerous bugs related to memory usage (OOM errors) and data alignment, ensuring a much smoother simulation and export experience. 

*Note: If you are using custom scripts, please note that "Audio" has been renamed to "Acoustic" in many classes and functions to better reflect the underlying physics models.*
