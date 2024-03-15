import os
from pathlib import Path
from typing import Optional

from anki.collection import Collection
from anki.models import ChangeNotetypeRequest
from anki.notes import Note, NoteId


def experimental_deck(col):
    root = col.sched.deck_due_tree()
    all_deck, = [c for c in root.children if c.name == "All"]
    experimental, = [c for c in all_deck.children if c.name == "Experimental"]
    return experimental


class VerseNote:
    def __init__(self, note: Note, col: Collection):
        self.col = col
        self.note = note

    def primary_value(self):
        return self.note["Reference"]

    def edit(self):
        note = self.note
        new_note = dict()
        new_note["Reference"] = note["Reference"].split("<br>")[0]
        new_note["Content"] = note["Content"].split("<br>")[0]
        if note["Reference"].endswith(".a"):
            new_note["Continued"] = "&gt;"
            next_note_reference = f"{note['Reference'][:-2]}.b"
            next_note_searchstring = f'"Reference:{next_note_reference}"'
            next_note_ids = self.col.find_notes(next_note_searchstring)
            if len(next_note_ids) == 1:
                next_note = self.col.get_note(next_note_ids[0])
                new_note["Next"] = next_note["Content"]
                new_note["Next Transcript"] = f"What's the next part?<br><br>{note['Content']}"
            elif len(next_note_ids) == 0:
                pass
            else:
                raise Exception(f"Found two notes with the same Reference: {next_note_reference}")
        new_note["Content"] = note["Content"].replace(" &gt;", "")
        new_note["Chapter Transcript"] = f"Which Bible chapter?<br><br>{note['Content']}"
        return new_note


class ChapterNote:
    def __init__(self, note: Note, col: Collection):
        self.col = col
        self.note = note

    def primary_value(self):
        return self.note["Reference"]

    def chapter_components(self):
        name, number = self.note["Reference"].split(" ")
        return name, number

    def next_chapter_note(self) -> Optional['ChapterNote']:
        this_name, this_number = self.chapter_components()
        this_number = int(this_number)
        next_note_reference = f"{this_name} {this_number + 1}"
        next_note_searchstring = f'"Reference:{next_note_reference}"'
        next_note_ids = self.col.find_notes(next_note_searchstring)
        if len(next_note_ids) == 1:
            next_note = self.col.get_note(next_note_ids[0])
            return ChapterNote(next_note, self.col)
        elif len(next_note_ids) == 0:
            return None
        else:
            raise Exception(f"Found two notes with the same Reference: {next_note_reference}")

    def edit(self):
        note = self.note
        new_note = dict()
        if "<img" in note["Summary"]:
            new_note["Picture"] = "<img" + note["Summary"].split("<img")[-1]
        new_note["Reference"] = note["Reference"].split("<br>")[0]
        new_note["Summary"] = note["Summary"].split("<br>")[0]
        next_note = self.next_chapter_note()
        if next_note is not None:
            new_note["Next summary"] = next_note.note["Summary"]
            new_note["Next picture"] = next_note.note["Picture"]
        return new_note


class Facade:
    def __init__(self):
        collection_path = os.path.join(Path.home(), ".local/share/Anki2/User 1/collection.anki2")
        self.col = Collection(collection_path)

    def old_change_note_type(self, sample_note: Note):
        inp = ChangeNotetypeRequest()
        old_note_type_id = sample_note.note_type()["id"]
        new_note_type_id = self.col.get_note(self.col.find_notes("deck:All::Experimental")[0]).mid
        change_note_type_info = self.col.models.change_notetype_info(
            old_notetype_id=old_note_type_id,
            new_notetype_id=new_note_type_id,
        )
        inp.ParseFromString(change_note_type_info.SerializeToString())
        # inp.note_ids.extend([sample_note.id])
        # inp.new_notetype_id = new_note_type_id
        self.col.models.change_notetype_of_notes(inp)
        x = 0

    def change_note_type(self, sample_note: Note):
        old_note_type_id = sample_note.note_type()["id"]
        new_note_type_id = self.col.get_note(self.col.find_notes("deck:All::Experimental")[0]).mid
        inp = ChangeNotetypeRequest(
            old_notetype_id=old_note_type_id,
            new_notetype_id=new_note_type_id,
            note_ids=[sample_note.id],
        )
        self.col.models.change_notetype_of_notes(inp)
        x = 0

    def sample_change_note_type(self):
        sample_note_id, = self.col.find_notes("deck:All::Experimental Psalm 999")
        sample_note = self.col.get_note(sample_note_id)
        self.old_change_note_type(sample_note)

    def sample_add_note(self):
        deck = self.col.decks.by_name("All::Experimental")

    def sample_edit_note(self):
        sample_note_id, = self.col.find_notes("deck:All::Experimental Psalm 999")
        sample_note = self.col.get_note(sample_note_id)
        sample_note["Reference"] = sample_note["Reference"].split("<br>")[0]
        sample_note["Content"] = sample_note["Content"].split("<br>")[0]
        for k, v in sample_note.items():
            print(f"{k} -> {v}")
        self.col.update_note(sample_note)

    def edit_note(self, anki_note: Note):
        note_type = anki_note.note_type()["name"]
        if note_type == "Verse":
            note = VerseNote(anki_note, self.col)
        elif note_type == "Chapter":
            note = ChapterNote(anki_note, self.col)
        else:
            raise Exception(f"Unknown note type: {note_type}")
        new_note = note.edit()
        for field in new_note:
            if field not in anki_note:
                raise Exception(f"Field '{field}' not in note {note.primary_value()}")
        print(f"Processing {note_type} note: {note.primary_value()}")
        for field in new_note:
            if anki_note[field] != new_note[field]:
                print(f"  Setting {field}:")
                print(f"  - {anki_note[field]}")
                print(f"  + {new_note[field]}")
                anki_note[field] = new_note[field]
        self.col.update_note(anki_note)

    def edit_all_notes(self):
        note_ids = self.col.find_notes("deck:Active::Theology_Temp")
        for note_id in note_ids:
            note = self.col.get_note(note_id)
            self.edit_note(note)


if __name__ == '__main__':
    facade = Facade()
    # facade.sample_change_note_type()
    # facade.sample_edit_note()
    facade.edit_all_notes()
