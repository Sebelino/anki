import os
from pathlib import Path

from anki.collection import Collection
from anki.models import ChangeNotetypeRequest
from anki.notes import Note


def experimental_deck(col):
    root = col.sched.deck_due_tree()
    all_deck, = [c for c in root.children if c.name == "All"]
    experimental, = [c for c in all_deck.children if c.name == "Experimental"]
    return experimental


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

    def edit_all_notes(self):
        note_ids = self.col.find_notes("deck:Active::Theology_Temp")
        for note_id in note_ids:
            note = self.col.get_note(note_id)
            new_note = dict()
            new_note["Reference"] = note["Reference"].split("<br>")[0]
            new_note["Content"] = note["Content"].split("<br>")[0]
            if note["Reference"].endswith(".a"):
                new_note["Continued"] = "&gt;"
            new_note["Content"] = note["Content"].replace(" &gt;", "")
            new_note["Chapter Transcript"] = f"Which Bible chapter?<br><br>{note['Content']}"
            for field in new_note:
                if field not in note:
                    raise Exception(f"Field '{field}' not in note {note['Reference']}")
            print(f"Updating note {note['Reference']}:")
            for field in new_note:
                if note[field] != new_note[field]:
                    print(f"  Setting {field}:")
                    print(f"  - {note[field]}")
                    print(f"  + {new_note[field]}")
                    note[field] = new_note[field]
            self.col.update_note(note)


if __name__ == '__main__':
    facade = Facade()
    # facade.sample_change_note_type()
    # facade.sample_edit_note()
    facade.edit_all_notes()
