import os


def convert_sh_to_lf():
    count = 0
    for root, _dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".sh"):
                path = os.path.join(root, file)
                # Read data first
                with open(path, "rb") as f:
                    data = f.read()
                # Replace line endings
                lf_data = data.replace(b"\r\n", b"\n")
                # Write back only if changed
                if lf_data != data:
                    with open(path, "wb") as f:
                        f.write(lf_data)
                    print(f"Converted {path} to LF line endings")
                    count += 1
    print(f"Finished. Converted {count} files.")


if __name__ == "__main__":
    convert_sh_to_lf()
