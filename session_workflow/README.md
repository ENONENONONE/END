# session_excerpts

The scripts, inputs and outputs of the session's checks:

| Folder | Contents |
|---|---|
| `bias/` | Circularity, forking, look-elsewhere, mentioned-value and Voynich checks, each with a `_verify` pass |
| `excerpts/` | Locating, rendering and translating pages of the manuscript, with controls |
| `spoken/` | Homophones, respelling and silent-letter tests |
| `vl/`, `voynich/` | The EVA transliteration `ZL3b-n.txt`, the plate's Latin, and their readers |
| `cmu/` | The CMU Pronouncing Dictionary and its licence |

No path in these files is tied to one machine. Where a script needs a file, you put in your own system path.

## Set your own paths

Two placeholders stand where machine paths were.

**`<scratchpad>`** stands for this `session_excerpts` folder; the subfolders it names (`vl/`, `cmu/`, `bias/`, `spoken/`) are the ones here. Replace it with this folder's full path on your system. 24 scripts use it. For example:

```python
SP = "<scratchpad>/"                                     # as found
SP = "/path/on/your/system/session_excerpts/"            # yours
```

**`~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/`** stands for the corpus folder: the folder holding `emerald_tablet.json`, `Voynich_Manuscript.pdf` and `cascade_corpus_review.html`. 33 scripts use it. Replace that part of the path with the folder where those files are on your system.

To find every line to change:

```bash
grep -rn -e '<scratchpad>' -e '~/Documents/' --include='*.py' .
```

Two of those files are public:

- `emerald_tablet.json`: https://cascade.training/assets/math/emerald_tablet.json
- `Voynich_Manuscript.pdf`: https://end.rito.one/solved/data/Voynich_Manuscript.pdf

## Removed, nothing to fill in

These mark personal or network details taken out. The scripts do not need them:

- `<address>`: a private or server network address
- `<mac>`: a device's hardware address
- `user@`: a login name

## Requirements

- Python 3
- `numpy`, `pillow`, `pypdf` and `beautifulsoup4`

```bash
python3 -m pip install numpy pillow pypdf beautifulsoup4
```

The scripts' own modules (`common`, `aligner`, `field`, `voy`, `glosses`, `load`, `tabula`) sit beside the scripts that import them.
