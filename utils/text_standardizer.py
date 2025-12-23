def parse_to_sections(text: str):
    import re

    sections = []
    current_section = {"title": None, "content": []}
    lines = text.split("\n")
    buffer = []

    YOUTUBE_REGEX = re.compile(
        r"(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w\-]+)"
    )
    LINK_REGEX = re.compile(r"(https?://[^\s]+)")

    INLINE_PATTERN = re.compile(
        r"(\*\*(.*?)\*\*|\*(.*?)\*|\$(.+?)\$)"
    )

    def flush_buffer():
        if not buffer:
            return
        paragraph = "\n".join(buffer).strip()
        buffer.clear()
        if not paragraph:
            return

        # Pure link line
        yt_match = YOUTUBE_REGEX.search(paragraph)

        if yt_match:
            current_section["content"].append({
                "type": "youtube",
                "value": yt_match.group(1)
            })
            return

        current_section["content"].append({
            "type": "paragraph",
            "value": parse_inline_formats(paragraph)
        })

    def parse_basic_inline(text):
        fragments = []
        last = 0

        for m in INLINE_PATTERN.finditer(text):
            start, end = m.span()
            if start > last:
                fragments.append({"type": "text", "value": text[last:start]})

            if m.group(2):
                fragments.append({"type": "bold", "value": m.group(2)})
            elif m.group(3):
                fragments.append({"type": "italic", "value": m.group(3)})
            elif m.group(4):
                fragments.append({"type": "math_inline", "value": m.group(4)})

            last = end

        if last < len(text):
            fragments.append({"type": "text", "value": text[last:]})

        return fragments


    def parse_inline_formats(text):
        fragments = []
        pos = 0

        for m in LINK_REGEX.finditer(text):
            start, end = m.span()

            if start > pos:
                fragments.extend(parse_basic_inline(text[pos:start]))

            fragments.append({
                "type": "link",
                "value": m.group(1)
            })

            pos = end

        if pos < len(text):
            fragments.extend(parse_basic_inline(text[pos:]))

        return fragments

    def is_title_line(idx):
        line = lines[idx].strip()

        if not line:
            return False

        # Reject lists and bullets
        if re.match(r"^(\d+\.\s+|-+\s+)", line):
            return False

        # Reject sentences (ends with punctuation)
        if re.search(r"[.!?]$", line):
            return False

        # Reject very long lines (likely paragraphs)
        if len(line) > 80:
            return False

        # Must be surrounded by blank lines (Markdown-style)
        if idx > 0 and lines[idx - 1].strip() != "":
            return False
        if idx < len(lines) - 1 and lines[idx + 1].strip() != "":
            return False

        # Reject obvious paragraph starters
        if re.match(r"^(To|This|Suppose|Given|Remember|You can)\b", line):
            return False

        return True


    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # Section title (plain text)
        if is_title_line(i):
            flush_buffer()
            if current_section["title"] or current_section["content"]:
                sections.append(current_section)
            current_section = {
                "title": line.strip(),
                "content": []
            }

        # Numbered list
        elif re.match(r"^\d+\.\s+", line):
            flush_buffer()
            item = re.sub(r"^\d+\.\s+", "", line)
            current_section["content"].append({
                "type": "list_item",
                "value": parse_inline_formats(item)
            })

        # Bullet list
        elif re.match(r"^-\s+", line):
            flush_buffer()
            item = re.sub(r"^-\s+", "", line)
            current_section["content"].append({
                "type": "bullet_point",
                "value": parse_inline_formats(item)
            })

        # Formula block
        elif line.strip().startswith("$$"):
            flush_buffer()
            if line.strip() == "$$":
                i += 1
                formula_lines = []
                while i < len(lines) and lines[i].strip() != "$$":
                    formula_lines.append(lines[i])
                    i += 1
                formula = "\n".join(formula_lines).strip()
            else:
                formula = line.strip().strip("$").strip()

            current_section["content"].append({
                "type": "formula_block",
                "value": formula
            })

        # Blank line
        elif line.strip() == "":
            flush_buffer()

        # Normal text
        else:
            buffer.append(line)

        i += 1

    flush_buffer()
    if current_section["title"] or current_section["content"]:
        sections.append(current_section)

    return sections



input = r"""Finding a Plane Through Given Points

To find a plane that passes through a set of given points, you need to determine the equation of the plane. The general equation of a plane in 3D space is given by **ax + by + cz + d = 0**, where **a**, **b**, **c**, and **d** are constants.

Steps to Find the Plane:

1. **Identify the Points**: Clearly mark the given points through which the plane passes.
2. **Find the Normal Vector**: To define a plane, you need a normal vector (**n = (a, b, c)**) and a point on the plane. If you have three points, you can find two vectors in the plane and then calculate their cross product to get the normal vector.
3. **Apply the Equation**: Use one of the points and the normal vector in the plane equation **a(x - x0) + b(y - y0) + c(z - z0) = 0**, where **(x0, y0, z0)** is a point on the plane.

Example Problem:

Suppose you have three points **P1(1, 2, 3)**, **P2(4, 5, 6)**, and **P3(7, 8, 9)**. Find the equation of the plane that passes through these points.

Solution:

1. **Find Vectors in the Plane**:
   - Vector **v1 = P2 - P1 = (4 - 1, 5 - 2, 6 - 3) = (3, 3, 3)**
   - Vector **v2 = P3 - P1 = (7 - 1, 8 - 2, 9 - 3) = (6, 6, 6)**

2. **Calculate the Normal Vector**:
   - **n = v1 × v2 = (3, 3, 3) × (6, 6, 6) = (0, 0, 0)**. This result indicates that **v1** and **v2** are parallel, suggesting the points are collinear (lie on the same line), and there are infinitely many planes that can pass through these points.

3. **Conclusion**:
   Given that **P1**, **P2**, and **P3** are collinear, we cannot define a unique plane through these points without additional information.

This example illustrates the process of attempting to find a plane through given points and highlights the importance of ensuring the points are not collinear.

Introduction to Miller Indices

Miller indices are a set of numbers used to describe the orientation of a plane in a crystal lattice. They are based on the intercepts of the plane with the crystal axes, measured in terms of the lattice constants.

Procedure for Finding Miller Indices:

1. **Find the Intercepts**: Identify where the plane intersects the x, y, and z axes.
2. **Take the Reciprocals**: Calculate the reciprocals of these intercepts.
3. **Reduce to Smallest Whole Numbers**: Reduce the fractions to their smallest whole number ratios.     

Miller Index Notation:
A plane that intersects the x, y, and z axes at **a**, **b**, and **c** lattice constants, respectively, has Miller indices of **(hkl)**, where **h = 1/a**, **k = 1/b**, and **l = 1/c**.

Drawing the Plane:
To draw a plane with given Miller indices, follow these steps:
1. **Find the Reciprocals**: Calculate the reciprocals of the Miller indices.
2. **Draw the Cube**: Draw a cube representing the crystal lattice.
3. **Mark the Intercepts**: Mark the intercepts on the axes according to the reciprocals of the Miller indices.
4. **Draw the Plane**: Draw the plane that passes through these intercepts.

Example Problem:
Consider a plane with Miller indices **(110)**. To draw this plane, first find the reciprocals of the indices, which are **1/1**, **1/1**, and **1/0** (since the index for the z-axis is 0, its reciprocal is infinity).

You can watch a video on how to visualize and draw planes with given Miller indices here: https://www.youtube.com/watch?v=629bin6Sqgw

Symmetry-Equivalent Surfaces:
In a cubic crystal system, there are 6 faces related by symmetry elements that are equivalent to the **(100)** surface. These surfaces can be denoted by the notation **{100}**, where the curly brackets indicate a set of symmetry-equivalent planes.

For more information on crystal structures and Miller indices, you can refer to this video: https://www.youtube.com/watch?v=xIuuTSJ5Dws

Remember, understanding Miller indices is crucial for describing the orientation of planes in crystal lattices, which is essential in materials science and crystallography.

"""

result = parse_to_sections(input)
print("Result: ", result)