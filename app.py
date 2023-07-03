import streamlit as st
import openai
import requests
from PIL import Image, ImageDraw, ImageFont
import textwrap

st.title("명언 생성기")
openai.api_key = st.secrets["apikey"]
with st.form("form"):
    submit = st.form_submit_button("명언 생성하기")

    if submit:
        # Fetch a random quote using an API
        response = requests.get("https://api.quotable.io/random")
        data = response.json()
        quote_text = data["content"] + " - " + data["author"]

        gpt_prompt = [
            {
                "role": "system",
                "content": "You are an art gallery docent with the unique ability to imagine and eloquently describe images based on simple words or phrases. Your goal is to portray these images in an artistic, picture-like style, creating a vivid mental image. Your descriptions should be concise, utilising rich vocabulary, and limited to approximately two sentences. Please respond in English.",
            },
            {
                "role": "user",
                "content": quote_text,
            },
        ]

        with st.spinner("이미지 생각 중..."):
            gpt_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=gpt_prompt
            )

        image_prompt = gpt_response["choices"][0]["message"]["content"]

        # Translate English image prompt to Korean
        translation_prompt = [
            {
                "role": "system",
                "content": "You are a highly skilled translator capable of translating English to Korean. Please translate the following text.",
            },
            {
                "role": "user",
                "content": quote_text,
            },
        ]

        with st.spinner("명언 번역 중..."):
            translation_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=translation_prompt
            )

        image_prompt_korean = translation_response["choices"][0]["message"]["content"]

        st.write(image_prompt_korean)
        with st.spinner("이미지 생성중..."):
            dalle_response = openai.Image.create(prompt=image_prompt, size="1024x1024")

        # Get the image URL
        image_url = dalle_response["data"][0]["url"]

        # Download the image
        img_data = requests.get(image_url).content
        with open("image.jpg", "wb") as handler:
            handler.write(img_data)

        # Open an image file
        with Image.open("image.jpg") as img:
            # Get image size
            img_width, img_height = img.size

            # Initialize ImageDraw
            d = ImageDraw.Draw(img)

            # Specify font and size
            fnt = ImageFont.truetype("./나눔손글씨 규리의 일기.ttf", 100)

            # Calculate text size
            text_width, text_height = fnt.getbbox(image_prompt_korean)[2:4]

            # Calculate the x and y coordinates for the text
            x = (img_width - text_width) / 2
            y = (img_height - text_height) / 2

            # If the text width is more than half of the image width, wrap the text
            # Calculate text width using getbbox
            if fnt.getbbox(image_prompt_korean)[2] > img_width / 2:
                lines = textwrap.wrap(
                    image_prompt_korean, width=int(img_width / 2 / fnt.getbbox(" ")[2])
                )
                y_temp = y
                for line in lines:
                    line_width, line_height = fnt.getbbox(line)[2:4]
                    d.text(
                        ((img_width - line_width) / 2, y_temp),
                        line,
                        font=fnt,
                        fill=(255, 255, 255),
                    )
                    y_temp += line_height
            else:
                # Add text to image
                offset = 2  # set the outline thickness
                x = (img_width - text_width) / 2
                y = (img_height - text_height) / 2

                # Add text outline
                for adj in [-offset, offset]:
                    d.text((x + adj, y), image_prompt_korean, font=fnt, fill="black")
                    d.text((x, y + adj), image_prompt_korean, font=fnt, fill="black")
                    d.text(
                        (x + adj, y + adj), image_prompt_korean, font=fnt, fill="black"
                    )
                    d.text(
                        (x - adj, y - adj), image_prompt_korean, font=fnt, fill="black"
                    )

                # Add original (white) text
                d.text((x, y), image_prompt_korean, font=fnt, fill=(255, 255, 255))

            # Save the image
            img.save("quote_image.jpg")

        # Display the image
        st.image("quote_image.jpg")
