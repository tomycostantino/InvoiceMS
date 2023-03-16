import fitz


def mark_word(page, text):
    """
    Underline each word that contains 'text'.
    """
    found = 0
    wlist = page.get_text("words")  # make the word list
    for w in wlist:                 # scan through all words on page
        if text in w[4]:            # w[4] is the word's string
            found += 1              # count
            r = fitz.Rect(w[:4])    # make rect from word bbox
            page.add_underline_annot(r)  # underline
    return found


def mark_doc(filename: str):
    doc = fitz.open(filename)
    iterable = [page.get_text('words') for page in doc]
    # Make a list that contains every word present in the document so it is marked
    word_list = [word[4] for word in iterable[0]]

    # Display them
    print(word_list)

    new_doc = False  # indicator if anything found at all

    for page in doc:  # scan through the pages
        for w in word_list:
            found = mark_word(page, w)  # mark the page's words
            if found:  # if anything found ...
                new_doc = True
                print("found '%s' %i times on page %i" % (w, found, page.number + 1))

    if new_doc:
        doc.save("marked-" + doc.name)


if __name__ == '__main__':
    mark_doc('sample.pdf')
