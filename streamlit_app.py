import replicate
import streamlit as st
import requests
import zipfile
import io
import base64
from streamlit_image_select import image_select
from typing import Any

# UI configurations
st.set_page_config(page_title="Replicate Image Generator",
                   page_icon=":bridge_at_night:",
                   layout="wide")
st.markdown("# :rainbow[GlowCorp Character Factory]🏭")

# API Tokens and endpoints from `.streamlit/secrets.toml` file
REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
REPLICATE_MODEL_FACE = st.secrets["REPLICATE_MODEL_FACE"]

# Placeholders for images and gallery
generated_images_placeholder = st.empty()
gallery_placeholder = st.empty()


# Predefined input data for the model
# Predefined input data for the model
PREDEFINED_INPUT = {
    "prompt": "Low poly pixelated of close-up of uploaded image, ps2 playstation psx gamecube game gta head 3d --style ddCHhSumaNyOrL1Q",
    "instant_id_strength": 0.8,
    "neg_prompt": "boring"  # Corrected indentation here
}

def configure_sidebar() -> None:
    """
    Setup and display the sidebar elements.

    This function configures the sidebar of the Streamlit application,
    including the form for user inputs and the resources section.
    """
    with st.sidebar:
        with st.form("my_form"):
            st.info("**Yo fam! Start here ↓**", icon="👋🏾")
            with st.expander(":rainbow[**Create your character**]"):
                # Advanced Settings (for the curious minds!)
                style = st.selectbox('Choose an image style', ("PS2", "Pixelated", "Clay", "Emoji", "3D"))
                uploaded_image = st.file_uploader("Upload an image file", type=["jpg", "jpeg", "png", "webp"])

            # The Big Red "Submit" Button!
            submitted = st.form_submit_button(
                "Submit", use_container_width=True)

            # Credits and resources
        st.markdown(
            """
            ---
            Follow 🚺 Curetique(owners of GlowCorp✨) on:

            Tiktok → [@curetique](https://www.tiktok.com/@curetique)

            """
        )

        return submitted, style, uploaded_image

def main_page(submitted: bool, style: str, uploaded_image: Any) -> None:
    """Main page layout and logic for generating images.

    Args:
        submitted (bool): Flag indicating whether the form has been submitted.
        uploaded_image (Any): The file-like object of the selected image.
    """
    if style == "PS2":
        style = "Video game"
    if style == "Pixelated":  # Corrected indentation here
        style = "Pixels"

    if submitted:
        with st.status('👩🏾‍🍳 Whipping up your character...', expanded=True) as status:
            st.write("⚙️ Model initiated")
            st.write("🙆‍♀️ Stand up and strecth in the meantime")
            try:
                # Only call the API if the "Submit" button was pressed
                if submitted:
                    # Convert the uploaded image to the required format
                    if uploaded_image is not None:
                        image_data = uploaded_image.read()
                        image_uri = f"data:image/jpeg;base64,{base64.b64encode(image_data).decode()}"
                    else:
                        st.error("Please select an image file.", icon="🚨")
                        return

                    # Calling the replicate API to get the image
                    with generated_images_placeholder.container():
                        all_images = []  # List to store all generated images
                        output = replicate.run(
                            REPLICATE_MODEL_FACE,
                            input={
                                "image": image_uri,
                                "style": style,
                                "prompt": PREDEFINED_INPUT["prompt"],
                                "neg_prompt": PREDEFINED_INPUT["neg_prompt"],
                                "instant_id_strength": PREDEFINED_INPUT["instant_id_strength"]
                            }
                        )
                        if output:
                            st.toast(
                                'Your character has been generated!', icon='😍')
                            # Save generated image to session state
                            st.session_state.generated_image = output

                            # Displaying the image
                            for image in st.session_state.generated_image:
                                with st.container():
                                    st.image(image, caption="Generated Image 🎈",
                                             use_column_width=True)
                                    # Add image to the list
                                    all_images.append(image)

                            # Save all generated images to session state
                            st.session_state.all_images = all_images

                            # Create a BytesIO object
                            zip_io = io.BytesIO()

                            # Download option for each image
                            with zipfile.ZipFile(zip_io, 'w') as zipf:
                                for i, image in enumerate(st.session_state.all_images):
                                    response = requests.get(image)
                                    if response.status_code == 200:
                                        image_data = response.content
                                        # Write each image to the zip file with a name
                                        zipf.writestr(
                                            f"output_file_{i+1}.png", image_data)
                                    else:
                                        st.error(
                                            f"Failed to fetch image {i+1} from {image}. Error code: {response.status_code}", icon="🚨")
                            # Create a download button for the zip file
                            st.download_button(
                                ":red[**Download All Images**]", data=zip_io.getvalue(), file_name="output_files.zip", mime="application/zip", use_container_width=True)
                    status.update(label="✅ Images generated!",
                                  state="complete", expanded=False)
            except Exception as e:
                print(e)
                st.error(f'Encountered an error: {e}', icon="🚨")

    # If not submitted, chill here 🍹
    else:
        pass

    # Footer
    st.divider()
    footer = """<div style="text-align: center;">
                <a href="https://visitorbadge.io/status?path=https%3A%2F%2FGlowCorp.streamlit.app%2F">
                    <img src="https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2FGlowCorp.streamlit.app%2F&label=GlowCorp&labelColor=%23ffffff&countColor=%23000000&style=plastic" />
                </a>
            </div>"""
    st.markdown(footer, unsafe_allow_html=True)

    # Gallery display for inspo
    with gallery_placeholder.container():
        img = image_select(
            label="(Click on the sidebar to get started! 😉)",
            images=[
                 "gallery/before.jpg", "gallery/after.jpg", ],
            captions=["before: unedited picture",
                      "after: new character unlocked",
                      ],
            use_container_width=True
        )

def main():
    """
    Main function to run the Streamlit application.

    This function initializes the sidebar configuration and the main page layout.
    It retrieves the user inputs from the sidebar, and passes them to the main page function.
    The main page function then generates images based on these inputs.
    """
    submitted, style, uploaded_image = configure_sidebar()
    main_page(submitted, style, uploaded_image)

if __name__ == "__main__":
    main()
