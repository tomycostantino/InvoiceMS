import os
from docx2pdf import convert


def main(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print(f"Reading files from {input_folder}...")
    for file in os.listdir(input_folder):
        print(f"Found file: {file}")
        if file.endswith(".docx"):
            input_path = os.path.join(input_folder, file)
            output_path = os.path.join(output_folder, file.replace(".docx", ".pdf"))
            print(f"Converting {input_path} to {output_path}")
            convert(input_path, output_path)

    print("Conversion completed!")


if __name__ == "__main__":
    main(input('Insert full path of word directory'), input('Insert path for PDF directory'))
