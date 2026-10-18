"""Cambridge 9701 nomenclature/equations course content for Vocogni.

Content is based on the user-provided 16-page Chemistry Master Note. The
marking rules are transparent practice rubrics, not official Cambridge
mark schemes. Keep chemistry content separate from Streamlit presentation.
"""
from __future__ import annotations


def _point(point_id, criteria, marks=1, **rules):
    return {"id": point_id, "criteria": criteria, "marks": marks, **rules}


def _open_question(qid, prompt, explanation, skill_tag, max_marks, points,
                   answer="", accepted_answers=None, typo_terms=None):
    question = {
        "id": qid,
        "type": "open_ended",
        "prompt": prompt,
        "answer": answer,
        "accepted_answers": list(accepted_answers or []),
        "explanation": explanation,
        "skill_tag": skill_tag,
        "mistake_tag": skill_tag,
        "max_marks": max_marks,
        "marking_points": points,
        "typo_terms": list(typo_terms or []),
        "marking_note": (
            "Practice rubric: credit is awarded for the listed evidence. "
            "Alternative scientifically valid wording can be reviewed if it "
            "does not match the configured criteria."
        ),
    }
    return question


def _lesson(number, title, explanation, worked_example, question, *,
            kind="standard", diagnostic=None):
    lesson_id = f"chem9701_l{number:02d}"
    record = {
        "id": lesson_id,
        "title": title,
        "kind": kind,
        "explanation": explanation,
        "worked_example": worked_example,
        "interactive_question": question,
        "questions": [question],
        "skill_ids": [question["skill_tag"]],
    }
    if diagnostic:
        record["diagnostic"] = diagnostic
    return record


def _diagnostic_question(qid, stage, skill, prompt, answer, explanation,
                         points, max_marks, typo_terms=None):
    question = _open_question(
        qid, prompt, explanation, skill, max_marks, points,
        answer=answer, typo_terms=typo_terms,
    )
    question["stage"] = stage
    return question


COURSE_DIAGNOSTIC = {
    "version": 1,
    "prerequisite_review": (
        "Review the difference between element symbols, subscripts, "
        "coefficients, and ionic charges. Then practise balancing charge "
        "before moving on to compound naming and equations."
    ),
    "questions": [
        _diagnostic_question(
            "chem9701_entry_d1", "prerequisite", "Chemical notation",
            "For Al₂(SO₄)₃, state the number of Al, S, and O atoms in one formula unit.",
            "Al = 2, S = 3, O = 12",
            "The subscript outside brackets multiplies every atom in SO₄: three sulfur atoms and twelve oxygen atoms.",
            [
                _point("al", "Identifies two aluminium atoms", regex_any=[r"(?:^|[^a-z])(?:al|aluminium|aluminum)(?:=|:|is)2(?:[^0-9]|$)"]),
                _point("s", "Identifies three sulfur atoms", regex_any=[r"(?:^|[^a-z])(?:s|sulfur|sulphur)(?:=|:|is)3(?:[^0-9]|$)"]),
                _point("o", "Identifies twelve oxygen atoms", regex_any=[r"(?:^|[^a-z])(?:o|oxygen)(?:=|:|is)12(?:[^0-9]|$)"]),
            ], 3
        ),
        _diagnostic_question(
            "chem9701_entry_d2", "level_1", "Compound naming",
            "Name FeCl₃ and explain how you know the Roman numeral.",
            "iron(III) chloride. Three Cl⁻ ions total −3, so iron is +3.",
            "Three chloride ions contribute a total charge of −3, so iron is +3 in this compound.",
            [
                _point("name", "Names iron(III) chloride", match_any=["iron(iii)chloride", "ironiii chloride", "iron 3 chloride"]),
                _point("charge", "Deducts an iron charge of +3 from three chloride ions", match_groups=[["three chloride", "3cl", "3 chloride"], ["+3", "positive 3", "iron is 3"]]),
            ], 2, ["chloride"]
        ),
        _diagnostic_question(
            "chem9701_entry_d3", "level_2", "Formula writing",
            "Write the formula for calcium hydroxide and explain the role of the brackets.",
            "Ca(OH)₂. Ca²⁺ is balanced by two OH⁻ ions, giving total charge zero; brackets group the repeated hydroxide ions.",
            "Ca²⁺ requires two OH⁻ ions; brackets show the hydroxide group is repeated twice.",
            [
                _point("formula", "Writes Ca(OH)₂", match_any=["ca(oh)2"]),
                _point("charge", "Explains the +2 calcium charge is balanced by two −1 hydroxide ions", match_groups=[["ca2+", "calcium +2", "calcium is +2"], ["two hydroxide", "2oh", "two oh"], ["neutral", "charge balances", "total charge zero"]]),
            ], 2, ["hydroxide", "hydrogen"]
        ),
        _diagnostic_question(
            "chem9701_entry_d4", "level_3", "Equation balancing",
            "Balance Fe + HCl → FeCl₂ + H₂. State what you changed.",
            "Fe + 2HCl → FeCl₂ + H₂. Change the coefficient before HCl; do not change subscripts.",
            "The coefficient 2 before HCl balances both chlorine atoms and hydrogen atoms without changing a subscript.",
            [
                _point("balanced", "Gives the balanced coefficient ratio 1:2:1:1", match_any=["fe+2hcl->fecl2+h2", "fe+2hcl→fecl2+h2"]),
                _point("method", "Says coefficients change, not subscripts", match_groups=[["coefficient", "coefficients"], ["not subscripts", "never change subscripts", "subscripts stay"]]),
            ], 2, ["coefficient", "subscript"]
        ),
        _diagnostic_question(
            "chem9701_entry_d5", "project", "Net ionic equations",
            "Write the net ionic equation for strong-acid/strong-alkali neutralisation and name the ions omitted from HCl + NaOH.",
            "H⁺(aq) + OH⁻(aq) → H₂O(l); Na⁺ and Cl⁻ are unchanged spectator ions.",
            "Na⁺ and Cl⁻ are unchanged spectator ions, so the net ionic equation is H⁺ + OH⁻ → H₂O.",
            [
                _point("net", "Writes H⁺ + OH⁻ → H₂O", match_any=["h++oh-->h2o", "h+(aq)+oh-(aq)->h2o(l)", "h+ + oh- -> h2o"]),
                _point("spectators", "Identifies Na⁺ and Cl⁻ as spectators", match_groups=[["na+", "sodium ion"], ["cl-", "chloride ion"], ["spectator", "unchanged"]]),
            ], 2, ["spectator", "chloride", "hydroxide"]
        ),
    ],
    "pathways": {
        "level_2": {
            "questions": [
                _open_question(
                    "chem9701_entry_l2",
                    "Write the formula of aluminium sulfate and show the charge calculation.",
                    "Two Al³⁺ ions and three SO₄²⁻ ions balance to zero charge, giving Al₂(SO₄)₃.",
                    "Formula writing", 2,
                    [
                        _point("formula", "Writes Al₂(SO₄)₃", match_any=["al2(so4)3"]),
                        _point("charge", "Shows 2(+3) + 3(−2) = 0", match_any=["2(+3)+3(-2)=0", "2*3+3*(-2)=0", "6-6=0", "two aluminium and three sulfate"]),
                    ],
                    answer="Al₂(SO₄)₃; 2(+3) + 3(−2) = 0",
                    typo_terms=["sulfate"],
                )
            ]
        },
        "level_3": {
            "questions": [
                _open_question(
                    "chem9701_entry_l3",
                    "Balance: 2Fe(NO₃)₃ + MgO → Fe₂O₃ + Mg(NO₃)₂. Explain how the nitrate groups help you balance it.",
                    "The balanced equation is 2Fe(NO₃)₃ + 3MgO → Fe₂O₃ + 3Mg(NO₃)₂. Nitrate remains intact on both sides, so it can be counted as a group.",
                    "Balancing equations", 2,
                    [
                        _point("equation", "Gives coefficients 2, 3, 1, 3", match_any=["2fe(no3)3+3mgo->fe2o3+3mg(no3)2", "2fe(no3)3+3mgo→fe2o3+3mg(no3)2"]),
                        _point("group", "Explains nitrate is unchanged and can be counted as a unit", match_groups=[["nitrate", "no3"], ["group", "unit", "intact", "unchanged"]]),
                    ],
                    answer="2Fe(NO₃)₃ + 3MgO → Fe₂O₃ + 3Mg(NO₃)₂. Nitrate stays intact on both sides and can be counted as a group.",
                    typo_terms=["nitrate", "nitrite"],
                )
            ]
        },
        "project": {
            "intro": "Apply formula writing, balancing, state symbols, and ionic reasoning to one reaction.",
            "questions": [
                _open_question(
                    "chem9701_entry_project",
                    "For BaCl₂(aq) + K₂SO₄(aq) → BaSO₄(s) + 2KCl(aq), write the net ionic equation and identify the precipitate.",
                    "Ba²⁺(aq) + SO₄²⁻(aq) → BaSO₄(s). Barium sulfate is the insoluble precipitate; K⁺ and Cl⁻ are spectators.",
                    "Ionic equations", 3,
                    [
                        _point("net", "Writes Ba²⁺ + SO₄²⁻ → BaSO₄(s)", match_any=["ba2++so42-->baso4(s)", "ba2+(aq)+so42-(aq)->baso4(s)"]),
                        _point("precipitate", "Identifies solid barium sulfate as the precipitate", match_groups=[["baso4", "barium sulfate"], ["solid", "(s)", "precipitate"]]),
                        _point("spectators", "Identifies K⁺ and Cl⁻ as spectator ions", match_groups=[["k+", "potassium ion"], ["cl-", "chloride ion"], ["spectator", "unchanged"]]),
                    ],
                    answer="Ba²⁺(aq) + SO₄²⁻(aq) → BaSO₄(s); K⁺ and Cl⁻ are spectators",
                    typo_terms=["sulfate", "precipitate"],
                )
            ]
        }
    }
}


LESSONS = [
    _lesson(
        1, "Formula Language and Ionic Charge",
        """
        <h3>1.1 Symbols, subscripts, brackets, coefficients, and charges</h3>
        <p>A chemical formula describes the types and ratios of atoms or ions. An element symbol uses a capital first letter and, where present, a lowercase second letter: <strong>Co</strong> is cobalt, whereas <strong>CO</strong> contains carbon and oxygen.</p>
        <ul>
          <li><strong>Subscript:</strong> counts atoms in one formula unit or molecule. H₂O contains two H atoms and one O atom.</li>
          <li><strong>Bracket subscript:</strong> multiplies every atom inside the brackets. Al₂(SO₄)₃ contains 2 Al, 3 S, and 12 O atoms.</li>
          <li><strong>Coefficient:</strong> multiplies the entire formula. 3Ca(OH)₂ contains 3 Ca, 6 O, and 6 H atoms.</li>
          <li><strong>Charge:</strong> the net electrical charge of an ion. SO₄²⁻ has charge −2; the 4 counts oxygen atoms.</li>
        </ul>
        <h3>1.2 Ions and charge balance</h3>
        <p>Cations are positively charged; anions are negatively charged. An ordinary ionic compound is electrically neutral: total positive charge plus total negative charge equals zero. Mg²⁺ and two Cl⁻ ions form MgCl₂. Two Al³⁺ ions and three O²⁻ ions form Al₂O₃.</p>
        <h3>1.3 Common charge patterns</h3>
        <ul>
          <li>Group 1 metals: usually +1; Group 2 metals: usually +2.</li>
          <li>Aluminium: commonly Al³⁺.</li>
          <li>Halogens: commonly −1; oxygen/sulfur family: commonly −2.</li>
          <li>Transition metals and some p-block metals can have variable oxidation states; use the Roman numeral or deduce the charge from neutrality.</li>
        </ul>
        <p>These are patterns, not replacements for reading the actual ion. Polyatomic ions have their own defined charges.</p>
        """,
        """
        <h4>Worked example: expand 3Ca(OH)₂</h4>
        <ol>
          <li>One Ca(OH)₂ contains 1 Ca, 2 O, and 2 H.</li>
          <li>The coefficient 3 multiplies all atoms: Ca = 3, O = 6, H = 6.</li>
          <li>For Al₂(SO₄)₃, the bracket subscript 3 gives S = 3 and O = 4 × 3 = 12, while Al = 2.</li>
        </ol>
        <p><strong>Check:</strong> changing a subscript changes the substance; changing a coefficient changes how many units are represented. Balance equations using coefficients only.</p>
        """,
        _open_question(
            "chem9701_l01_q", "Explain the meaning of the subscript in Al₂(SO₄)₃ and state the total number of Al, S, and O atoms. Also distinguish a coefficient from a subscript.",
            "There are 2 Al, 3 S, and 12 O atoms. The bracket subscript multiplies atoms in SO₄. A coefficient multiplies the entire formula; a subscript defines the composition of a substance.",
            "Formula notation", 5,
            [
                _point("al", "States Al = 2", regex_any=[r"(?:^|[^a-z])(?:al|aluminium|aluminum)(?:=|:|is)2(?:[^0-9]|$)"]),
                _point("s", "States S = 3", regex_any=[r"(?:^|[^a-z])(?:s|sulfur|sulphur)(?:=|:|is)3(?:[^0-9]|$)"]),
                _point("o", "States O = 12", regex_any=[r"(?:^|[^a-z])(?:o|oxygen)(?:=|:|is)12(?:[^0-9]|$)"]),
                _point("bracket", "Explains the 3 multiplies the entire SO₄ group", match_groups=[["3", "three"], ["bracket", "so4", "group"], ["multiply", "times", "each"]]),
                _point("coefficient", "Distinguishes coefficient from subscript", match_groups=[["coefficient"], ["whole formula", "entire formula", "number of units", "number of molecules"], ["subscript"], ["atoms", "atom ratio", "atom ratios", "atom count", "composition", "identity"]]),
            ],
            answer="Al = 2, S = 3, O = 12. The bracket subscript 3 multiplies every atom in SO₄. A coefficient multiplies the whole formula; a subscript defines the atom ratio and substance composition.",
        ),
        diagnostic=COURSE_DIAGNOSTIC,
    ),
    _lesson(
        2, "Naming Compounds",
        """
        <h3>Choose the naming system first</h3>
        <ul>
          <li><strong>Type I binary ionic:</strong> a metal with one common charge plus a non-metal. Keep the metal name; change the non-metal root to <em>-ide</em>. Examples: KCl, potassium chloride; MgBr₂, magnesium bromide; BaO, barium oxide; AlCl₃, aluminium chloride; Na₂S, sodium sulfide.</li>
          <li><strong>Type II binary ionic:</strong> a metal with variable charge. Name the cation, add its oxidation state as a Roman numeral in brackets, then name the anion with <em>-ide</em>.</li>
          <li><strong>Binary molecular:</strong> two non-metals. Use numerical prefixes; the second element ends in <em>-ide</em>. Do not use ionic charge balancing for this naming system.</li>
          <li>When a polyatomic ion is present, use its established name unchanged.</li>
        </ul>
        <h3>Variable-charge examples</h3>
        <ul>
          <li>FeCl₂: two Cl⁻ give −2, so iron is +2: iron(II) chloride.</li>
          <li>FeCl₃: three Cl⁻ give −3, so iron is +3: iron(III) chloride.</li>
          <li>CuBr: copper(I) bromide; PbO₂: lead(IV) oxide; CuO: copper(II) oxide.</li>
        </ul>
        <h3>Molecular prefixes</h3>
        <p>1 mono-, 2 di-, 3 tri-, 4 tetra-, 5 penta-, 6 hexa-, 7 hepta-, 8 octa-, 9 nona-, 10 deca-. Usually omit mono- from the first element, but name the second element with a prefix and an -ide ending.</p>
        <p>Examples: CO carbon monoxide; CO₂ carbon dioxide; SF₆ sulfur hexafluoride; N₂O₄ dinitrogen tetroxide; N₂O₅ dinitrogen pentoxide; PBr₅ phosphorus pentabromide. “Tetraoxide” contracts to “tetroxide”.</p>
        """,
        """
        <h4>Worked example: FeCl₃ and N₂O₄</h4>
        <ol>
          <li>FeCl₃ is ionic. Each chloride is −1, so three chloride ions total −3. Iron must be +3: iron(III) chloride.</li>
          <li>N₂O₄ contains two non-metals, so use prefixes rather than ionic charges: di-nitrogen and tetra-oxide, written dinitrogen tetroxide.</li>
        </ol>
        <p><strong>Decision check:</strong> identify the type before naming. Roman numerals describe oxidation state for a variable-charge metal; they do not count metal atoms.</p>
        """,
        _open_question(
            "chem9701_l02_q", "Name FeCl₂ and FeCl₃. Explain why the names differ, and name CO₂ and N₂O₄ using molecular prefixes.",
            "FeCl₂ is iron(II) chloride; FeCl₃ is iron(III) chloride. The metal charge differs because each chloride is −1. CO₂ is carbon dioxide and N₂O₄ is dinitrogen tetroxide.",
            "Compound naming", 5,
            [
                _point("fe2", "Names FeCl₂ iron(II) chloride", match_any=["iron(ii)chloride", "iron(2)chloride", "ironii chloride"]),
                _point("fe3", "Names FeCl₃ iron(III) chloride", match_any=["iron(iii)chloride", "iron(3)chloride", "ironiii chloride"]),
                _point("charge", "Explains chloride is −1 and the total chloride charge differs", match_groups=[["chloride"], ["-1", "negative one"], ["+2", "iron(ii)", "+3", "iron(iii)", "total charge"]]),
                _point("co2", "Names CO₂ carbon dioxide", match_any=["carbon dioxide"]),
                _point("n2o4", "Names N₂O₄ dinitrogen tetroxide", match_any=["dinitrogen tetroxide", "dinitrogen tetraoxide"]),
            ],
            answer="FeCl₂ is iron(II) chloride; FeCl₃ is iron(III) chloride; CO₂ is carbon dioxide; N₂O₄ is dinitrogen tetroxide. Each Cl⁻ is −1, so Fe is +2 in FeCl₂ and +3 in FeCl₃.",
            typo_terms=["chloride", "chlorate", "dioxide", "tetroxide"],
        ),
    ),
    _lesson(
        3, "Polyatomic Ions and Formula Construction",
        """
        <h3>Treat each polyatomic ion as one charged group</h3>
        <p>A polyatomic ion is a group of bonded atoms with an overall charge. In an ionic formula, the group remains intact. The compound is neutral overall, but the polyatomic ion keeps its charge.</p>
        <table>
          <tr><th>Formula</th><th>Name</th><th>Charge</th></tr>
          <tr><td>NH₄⁺</td><td>ammonium</td><td>+1</td></tr>
          <tr><td>OH⁻</td><td>hydroxide</td><td>−1</td></tr>
          <tr><td>NO₃⁻</td><td>nitrate</td><td>−1</td></tr>
          <tr><td>NO₂⁻</td><td>nitrite</td><td>−1</td></tr>
          <tr><td>HCO₃⁻</td><td>hydrogencarbonate / bicarbonate</td><td>−1</td></tr>
          <tr><td>CO₃²⁻</td><td>carbonate</td><td>−2</td></tr>
          <tr><td>SO₄²⁻</td><td>sulfate</td><td>−2</td></tr>
          <tr><td>SO₃²⁻</td><td>sulfite</td><td>−2</td></tr>
          <tr><td>PO₄³⁻</td><td>phosphate</td><td>−3</td></tr>
          <tr><td>PO₃³⁻</td><td>phosphite</td><td>−3</td></tr>
          <tr><td>CrO₄²⁻</td><td>chromate</td><td>−2</td></tr>
          <tr><td>CH₃COO⁻</td><td>ethanoate / acetate</td><td>−1</td></tr>
        </table>
        <p>The -ite ion in the nitrate/nitrite and sulfate/sulfite pairs has one fewer oxygen atom than its -ate counterpart in the pairs listed. Always preserve the actual formula and charge.</p>
        <h3>Writing a formula</h3>
        <ol>
          <li>Write the correct cation and anion with charges.</li>
          <li>Choose the smallest whole-number ratio giving total charge zero.</li>
          <li>If more than one complete polyatomic ion is needed, use brackets before the subscript.</li>
          <li>Check atom counts and the net charge.</li>
        </ol>
        <p>Examples: calcium hydroxide Ca(OH)₂; magnesium nitrate Mg(NO₃)₂; aluminium sulfate Al₂(SO₄)₃; ammonium phosphate (NH₄)₃PO₄; calcium phosphate Ca₃(PO₄)₂; iron(III) nitrate Fe(NO₃)₃.</p>
        """,
        """
        <h4>Worked example: aluminium sulfate</h4>
        <ol>
          <li>Use Al³⁺ and SO₄²⁻.</li>
          <li>The lowest total charge that matches is +6 and −6: two Al³⁺ ions and three sulfate ions.</li>
          <li>Write Al₂(SO₄)₃. The bracketed sulfate group occurs three times, giving 2 Al, 3 S and 12 O atoms.</li>
        </ol>
        <p>Brackets are needed in Ca(OH)₂ because two complete hydroxide ions are present. They do not mean the group becomes a separate molecule.</p>
        """,
        _open_question(
            "chem9701_l03_q", "Write the formulae for calcium hydroxide, magnesium nitrate, aluminium sulfate, ammonium phosphate, calcium phosphate, and iron(III) nitrate. Explain why brackets are required in at least two of them.",
            "Ca(OH)₂; Mg(NO₃)₂; Al₂(SO₄)₃; (NH₄)₃PO₄; Ca₃(PO₄)₂; Fe(NO₃)₃. Brackets show that a complete polyatomic ion is repeated.",
            "Polyatomic ions and formulae", 8,
            [
                _point("caoh", "Writes Ca(OH)₂", match_any=["ca(oh)2"]),
                _point("mgno3", "Writes Mg(NO₃)₂", match_any=["mg(no3)2"]),
                _point("al2so4", "Writes Al₂(SO₄)₃", match_any=["al2(so4)3"]),
                _point("ammonium", "Writes (NH₄)₃PO₄", match_any=["(nh4)3po4"]),
                _point("phosphate", "Writes Ca₃(PO₄)₂", match_any=["ca3(po4)2"]),
                _point("iron", "Writes Fe(NO₃)₃", match_any=["fe(no3)3"]),
                _point("brackets", "Explains brackets multiply/retain a whole polyatomic ion", match_groups=[["bracket", "parenthes"], ["whole", "complete", "group", "ion"], ["repeat", "multipl", "number of"]]),
                _point("neutral", "Connects formula ratios to charge neutrality", match_groups=[["charge"], ["zero", "neutral", "balance"]]),
            ],
            answer="Ca(OH)₂; Mg(NO₃)₂; Al₂(SO₄)₃; (NH₄)₃PO₄; Ca₃(PO₄)₂; Fe(NO₃)₃. Brackets multiply an entire repeated polyatomic ion. Each ionic formula has total charge zero.",
            typo_terms=["nitrate", "sulfate", "phosphate", "hydroxide"],
        ),
    ),
    _lesson(
        4, "Acid Nomenclature",
        """
        <h3>The anion determines the acid name</h3>
        <ul>
          <li><strong>Anion contains no oxygen:</strong> hydro- + anion root + -ic acid. Examples: HBr(aq), hydrobromic acid; HCl(aq), hydrochloric acid.</li>
          <li><strong>Oxyanion ends in -ate:</strong> change -ate to -ic acid and do not add hydro-. NO₃⁻ gives HNO₃, nitric acid; SO₄²⁻ gives H₂SO₄, sulfuric acid; PO₄³⁻ gives H₃PO₄, phosphoric acid.</li>
          <li><strong>Oxyanion ends in -ite:</strong> change -ite to -ous acid and do not add hydro-. SO₃²⁻ gives H₂SO₃, sulfurous acid; NO₂⁻ gives HNO₂, nitrous acid.</li>
        </ul>
        <p>This is a naming pattern, not a substitute for charge balancing. Distinguish HBr(g), hydrogen bromide gas, from HBr(aq), hydrobromic acid in water.</p>
        """,
        """
        <h4>Worked comparison: HNO₃ and HNO₂</h4>
        <ol>
          <li>HNO₃ contains nitrate, NO₃⁻, which ends in -ate: nitric acid.</li>
          <li>HNO₂ contains nitrite, NO₂⁻, which ends in -ite: nitrous acid.</li>
          <li>For HBr, the state matters: HBr(g) is hydrogen bromide; HBr(aq) is hydrobromic acid.</li>
        </ol>
        """,
        _open_question(
            "chem9701_l04_q", "Name HCl(aq), HBr(aq), HBr(g), HNO₃, HNO₂, H₂SO₄, H₂SO₃, and H₃PO₄. State the naming rule for -ate and -ite oxyanions.",
            "Hydrochloric acid; hydrobromic acid; hydrogen bromide gas; nitric acid; nitrous acid; sulfuric acid; sulfurous acid; phosphoric acid. -ate becomes -ic acid and -ite becomes -ous acid, with no hydro- for oxyacids.",
            "Acid nomenclature", 7,
            [
                _point("hcl", "Names HCl(aq) hydrochloric acid", match_any=["hydrochloric acid"]),
                _point("hbr_aq", "Names HBr(aq) hydrobromic acid", match_any=["hydrobromic acid"]),
                _point("hbr_g", "Distinguishes HBr(g) as hydrogen bromide gas", match_groups=[["hydrogen bromide"], ["gas", "(g)"]]),
                _point("nitric_nitrous", "Names HNO₃ nitric acid and HNO₂ nitrous acid", match_groups=[["nitric acid"], ["nitrous acid"]]),
                _point("sulfuric_sulfurous", "Names H₂SO₄ sulfuric acid and H₂SO₃ sulfurous acid", match_groups=[["sulfuric acid"], ["sulfurous acid"]]),
                _point("phosphoric", "Names H₃PO₄ phosphoric acid", match_any=["phosphoric acid"]),
                _point("suffix", "States -ate → -ic and -ite → -ous, without hydro- for oxyacids", match_groups=[["ate"], ["ic acid", "-ic"], ["ite"], ["ous acid", "-ous"], ["no hydro", "without hydro", "not hydro"]]),
            ],
            answer="HCl(aq) is hydrochloric acid; HBr(aq) is hydrobromic acid; HBr(g) is hydrogen bromide gas; HNO₃ is nitric acid; HNO₂ is nitrous acid; H₂SO₄ is sulfuric acid; H₂SO₃ is sulfurous acid; H₃PO₄ is phosphoric acid. -ate becomes -ic acid and -ite becomes -ous acid; oxyacids do not use hydro-.",
            typo_terms=["hydrochloric", "hydrobromic", "nitric", "nitrous", "sulfuric", "sulfurous", "phosphoric"],
        ),
    ),
    _lesson(
        5, "The Two-Way Name–Formula Translation System",
        """
        <h3>Name → formula</h3>
        <ol>
          <li>Classify the name: ionic, molecular, or acid.</li>
          <li>For ionic compounds, write the exact ions and charges. A Roman numeral gives the charge/oxidation state for the variable-charge metal.</li>
          <li>Choose the smallest ratio that makes total charge zero.</li>
          <li>Keep polyatomic ions intact and use parentheses when more than one is required.</li>
          <li>For molecular compounds, translate prefixes directly into subscripts.</li>
          <li>Check atom counts and, for ionic compounds, zero total charge.</li>
        </ol>
        <h3>Formula → name</h3>
        <ol>
          <li>Classify from the elements and groups.</li>
          <li>Name the cation or first element, then the anion or second element.</li>
          <li>Deduce a variable metal charge from neutrality and include its Roman numeral.</li>
          <li>Use a polyatomic ion's established name; apply acid rules when relevant.</li>
        </ol>
        <p>Roman numerals state oxidation state, not atom count. The charge-balancing algorithm does not apply to molecular prefixes.</p>
        """,
        """
        <h4>Worked comparison: copper(I) sulfate and copper(II) sulfate</h4>
        <ul>
          <li>Copper(I) sulfate: Cu⁺ and SO₄²⁻; two Cu⁺ ions balance one sulfate ion, so formula Cu₂SO₄.</li>
          <li>Copper(II) sulfate: Cu²⁺ and SO₄²⁻ balance 1:1, so formula CuSO₄.</li>
        </ul>
        <p>The sulfate ion is the same in both compounds; the copper charge changes the required ratio.</p>
        """,
        _open_question(
            "chem9701_l05_q", "Write the formulae for copper(I) sulfate and copper(II) sulfate. Explain how the Roman numeral changes the formula, then give a step-by-step rule for converting an ionic name into a formula.",
            "Copper(I) sulfate is Cu₂SO₄; copper(II) sulfate is CuSO₄. The numeral gives the copper charge, which must balance sulfate's −2 charge.",
            "Name–formula translation", 5,
            [
                _point("cu1", "Writes Cu₂SO₄ for copper(I) sulfate", match_any=["cu2so4"]),
                _point("cu2", "Writes CuSO₄ for copper(II) sulfate", match_any=["cuso4"]),
                _point("roman", "Explains Roman numeral is the metal oxidation state/charge, not atom count", match_groups=[["roman numeral"], ["charge", "oxidation state"], ["not", "rather than"], ["atom count", "number of atoms"]]),
                _point("ions", "Says identify ions and their charges", match_groups=[["ion"], ["charge"]]),
                _point("balance", "Says choose a smallest ratio that makes total charge zero", match_groups=[["ratio", "subscript"], ["zero", "neutral", "balance"]]),
            ],
            answer="Copper(I) sulfate is Cu₂SO₄; copper(II) sulfate is CuSO₄. The Roman numeral gives the copper charge, not atom count. Identify ions, balance total charge to zero, keep polyatomic groups intact, then check.",
            typo_terms=["sulfate", "oxidation"],
        ),
    ),
    _lesson(
        6, "Word Equations and Balancing",
        """
        <h3>Word equation → formula equation → balanced equation</h3>
        <ol>
          <li>Identify reactants (left) and products (right).</li>
          <li>Translate every substance name into its correct formula before balancing.</li>
          <li>Write the unbalanced formula equation.</li>
          <li>Change coefficients in front of formulae; never change subscripts.</li>
          <li>Recount every atom and reduce to the smallest whole-number ratio.</li>
          <li>Add state symbols if required.</li>
        </ol>
        <p>Useful method: start with a complex formula or an intact polyatomic group where convenient; for combustion, balance C, then H, then O. These are strategies, not absolute laws. The final audit must count every element.</p>
        <h3>Worked equations from the practice material</h3>
        <ul>
          <li>Iron + hydrochloric acid: Fe(s) + 2HCl(aq) → FeCl₂(aq) + H₂(g).</li>
          <li>Heating aluminium hydroxide: 2Al(OH)₃(s) → Al₂O₃(s) + 3H₂O(g).</li>
          <li>Hexane combustion: 2C₆H₁₄ + 19O₂ → 12CO₂ + 14H₂O.</li>
          <li>Calcium carbonate + hydrochloric acid: CaCO₃(s) + 2HCl(aq) → CaCl₂(aq) + H₂O(l) + CO₂(g).</li>
          <li>Complex example: 2Fe(NO₃)₃ + 3MgO → Fe₂O₃ + 3Mg(NO₃)₂.</li>
        </ul>
        """,
        """
        <h4>Worked example: calcium carbonate and hydrochloric acid</h4>
        <ol>
          <li>Write the formulas: CaCO₃ + HCl → CaCl₂ + H₂O + CO₂.</li>
          <li>Calcium, carbon and oxygen are consistent as written. CaCl₂ requires two chlorine atoms, so place 2 before HCl.</li>
          <li>The two H atoms then form one H₂O. The carbonate's three oxygen atoms are divided between H₂O and CO₂.</li>
          <li>Final equation: CaCO₃(s) + 2HCl(aq) → CaCl₂(aq) + H₂O(l) + CO₂(g).</li>
        </ol>
        <p>Audit atom counts on both sides. Never alter a formula to make the counts fit.</p>
        """,
        _open_question(
            "chem9701_l06_q", "Aqueous hydrochloric acid reacts with solid calcium carbonate to form aqueous calcium chloride, liquid water and carbon dioxide gas. Write the balanced equation with state symbols, then explain your balancing method.",
            "CaCO₃(s) + 2HCl(aq) → CaCl₂(aq) + H₂O(l) + CO₂(g). Coefficients balance atoms; formulas/subscripts remain unchanged.",
            "Equation construction and balancing", 5,
            [
                _point("reactants", "Writes CaCO₃ and HCl as reactants", match_groups=[["caco3"], ["hcl"]]),
                _point("products", "Writes CaCl₂, H₂O, and CO₂ as products", match_groups=[["cacl2"], ["h2o"], ["co2"]]),
                _point("coefficients", "Uses coefficient 2 before HCl", match_any=["2hcl", "2 hcl"]),
                _point("states", "Assigns (s), (aq), (l), and (g) consistently", match_groups=[["caco3(s)", "caco3 (s)"], ["hcl(aq)", "hcl (aq)"], ["h2o(l)", "h2o (l)"], ["co2(g)", "co2 (g)"]]),
                _point("method", "Explains coefficients changed and subscripts were not changed", match_groups=[["coefficient"], ["not subscripts", "subscripts unchanged", "don't change subscripts", "do not change subscripts"]]),
            ],
            answer="CaCO₃(s) + 2HCl(aq) → CaCl₂(aq) + H₂O(l) + CO₂(g). Balance with coefficients only; do not change subscripts because they define the substances.",
            typo_terms=["coefficient", "subscript", "carbonate"],
        ),
    ),
    _lesson(
        7, "State Symbols and Solubility",
        """
        <h3>State symbols</h3>
        <ul>
          <li><strong>(s):</strong> solid, including an insoluble precipitate.</li>
          <li><strong>(l):</strong> pure substance in the liquid state under the stated conditions.</li>
          <li><strong>(g):</strong> gas.</li>
          <li><strong>(aq):</strong> substance dissolved in water; it does not simply mean liquid.</li>
        </ul>
        <p>Use states specified by the question first. “Aqueous solution” or “dissolved in water” normally means (aq); powder, solid metal or precipitate indicates (s); a named gas or gas bubbles indicates (g). If states are absent, infer from physical state, reaction context, and solubility.</p>
        <h3>Useful solubility patterns and exceptions</h3>
        <ul>
          <li>Group 1 and ammonium salts are soluble.</li>
          <li>All nitrates are soluble.</li>
          <li>Most chlorides, bromides and iodides are soluble; AgCl and PbCl₂ are common exceptions.</li>
          <li>Most sulfates are soluble; BaSO₄ and PbSO₄ are insoluble, while CaSO₄ is sparingly soluble.</li>
          <li>Most carbonates and phosphates are insoluble unless paired with Group 1 or NH₄⁺.</li>
          <li>Most hydroxides are insoluble; Group 1 hydroxides are soluble. Calcium, strontium and barium hydroxides have varying/limited solubility.</li>
        </ul>
        <p>These are prediction rules. Explicit states or observations in a question take priority.</p>
        """,
        """
        <h4>Worked example: predict the barium sulfate state</h4>
        <p>BaCl₂(aq) and K₂SO₄(aq) supply Ba²⁺ and SO₄²⁻ ions. Barium sulfate is insoluble, so it forms BaSO₄(s). Potassium chloride stays dissolved: KCl(aq).</p>
        <p>Balanced equation: BaCl₂(aq) + K₂SO₄(aq) → BaSO₄(s) + 2KCl(aq).</p>
        <p>Do not label every solution (l): (aq) identifies dissolved material; (l) identifies a pure liquid.</p>
        """,
        _open_question(
            "chem9701_l07_q", "For BaCl₂(aq) + K₂SO₄(aq) → BaSO₄ + KCl, complete the balanced equation with state symbols. Explain why the barium sulfate state differs from potassium chloride.",
            "BaCl₂(aq) + K₂SO₄(aq) → BaSO₄(s) + 2KCl(aq). Barium sulfate is insoluble and precipitates; potassium salts remain soluble.",
            "State symbols and solubility", 4,
            [
                _point("balanced", "Balances the equation with coefficient 2 on KCl", match_any=["baCl2(aq)+k2so4(aq)->baso4(s)+2kcl(aq)", "bacl2(aq)+k2so4(aq)→baso4(s)+2kcl(aq)"]),
                _point("aq", "Labels reactants as aqueous", match_groups=[["bacl2(aq)", "bacl2 (aq)"], ["k2so4(aq)", "k2so4 (aq)"]]),
                _point("precipitate", "Labels BaSO₄ as solid precipitate", match_groups=[["baso4(s)", "baso4 (s)"], ["insoluble", "precipitate"]]),
                _point("kcl", "Labels KCl aqueous and explains it remains dissolved", match_groups=[["kcl(aq)", "kcl (aq)"], ["soluble", "dissolved", "potassium salts"]]),
            ],
            answer="BaCl₂(aq) + K₂SO₄(aq) → BaSO₄(s) + 2KCl(aq). Barium sulfate is insoluble and forms a precipitate; potassium chloride remains dissolved.",
            typo_terms=["sulfate", "precipitate", "aqueous"],
        ),
    ),
    _lesson(
        8, "Complete and Net Ionic Equations",
        """
        <h3>The four-step method</h3>
        <ol>
          <li>Write and balance the formula equation, including state symbols.</li>
          <li>Split soluble aqueous strong electrolytes into ions with correct charges and coefficients.</li>
          <li>Do not split solids, liquids, gases, precipitates, or substances that remain as molecules under the course convention (for example, water).</li>
          <li>Cancel identical ions on both sides. The remaining equation is the net ionic equation.</li>
        </ol>
        <p>A spectator ion remains unchanged. It must match on both sides in formula, charge, and state. A net ionic equation preserves atoms and total charge.</p>
        <h3>Reference examples</h3>
        <p><strong>Zinc displacement:</strong> Zn(s) + CuSO₄(aq) → ZnSO₄(aq) + Cu(s), giving Zn(s) + Cu²⁺(aq) → Zn²⁺(aq) + Cu(s). Sulfate is the spectator.</p>
        <p><strong>Barium sulfate precipitation:</strong> BaCl₂(aq) + K₂SO₄(aq) → BaSO₄(s) + 2KCl(aq), giving Ba²⁺(aq) + SO₄²⁻(aq) → BaSO₄(s). K⁺ and Cl⁻ are spectators.</p>
        <p><strong>Neutralisation:</strong> HCl(aq) + NaOH(aq) → NaCl(aq) + H₂O(l), giving H⁺(aq) + OH⁻(aq) → H₂O(l). Na⁺ and Cl⁻ are spectators.</p>
        <p><strong>Acid + carbonate:</strong> CaCO₃(s) + 2HCl(aq) → CaCl₂(aq) + H₂O(l) + CO₂(g), with net ionic form CaCO₃(s) + 2H⁺(aq) → Ca²⁺(aq) + H₂O(l) + CO₂(g).</p>
        """,
        """
        <h4>Worked example: barium sulfate precipitation</h4>
        <ol>
          <li>Start with BaCl₂(aq) + K₂SO₄(aq) → BaSO₄(s) + 2KCl(aq).</li>
          <li>Split the soluble aqueous salts: Ba²⁺ + 2Cl⁻ + 2K⁺ + SO₄²⁻ → BaSO₄(s) + 2K⁺ + 2Cl⁻.</li>
          <li>Cancel K⁺ and Cl⁻, which are identical on both sides.</li>
          <li>Net ionic equation: Ba²⁺(aq) + SO₄²⁻(aq) → BaSO₄(s).</li>
        </ol>
        <p>Check charge: +2 plus −2 is zero on the left, and the solid product is neutral.</p>
        """,
        _open_question(
            "chem9701_l08_q", "Write the complete ionic equation and net ionic equation for BaCl₂(aq) + K₂SO₄(aq) → BaSO₄(s) + 2KCl(aq). Name the spectator ions and justify their cancellation.",
            "Complete: Ba²⁺ + 2Cl⁻ + 2K⁺ + SO₄²⁻ → BaSO₄(s) + 2K⁺ + 2Cl⁻. Net: Ba²⁺ + SO₄²⁻ → BaSO₄(s). K⁺ and Cl⁻ are spectators.",
            "Ionic equations", 5,
            [
                _point("complete_left", "Dissociates aqueous reactants into Ba²⁺, 2Cl⁻, 2K⁺, SO₄²⁻", match_groups=[["ba2+"], ["2cl-", "2cl"], ["2k+", "2k"], ["so42-"]]),
                _point("product", "Leaves BaSO₄(s) intact and dissociates 2KCl(aq)", match_groups=[["baso4(s)", "baso4 (s)"], ["2k+", "2k"], ["2cl-", "2cl"]]),
                _point("net", "Writes Ba²⁺ + SO₄²⁻ → BaSO₄(s)", match_any=["ba2++so42-->baso4(s)", "ba2+(aq)+so42-(aq)->baso4(s)"]),
                _point("spectators", "Identifies K⁺ and Cl⁻ as spectators", match_groups=[["k+", "potassium"], ["cl-", "chloride"], ["spectator", "unchanged"]]),
                _point("why", "Explains identical ions cancel because unchanged on both sides", match_groups=[["same", "identical"], ["both sides"], ["unchanged", "spectator"]]),
            ],
            answer="Complete: Ba²⁺ + 2Cl⁻ + 2K⁺ + SO₄²⁻ → BaSO₄(s) + 2K⁺ + 2Cl⁻. Net: Ba²⁺ + SO₄²⁻ → BaSO₄(s). K⁺ and Cl⁻ are spectators because the same ions remain unchanged on both sides.",
            typo_terms=["sulfate", "spectator", "aqueous"],
        ),
    ),
    _lesson(
        9, "Titration and Mole Ratios",
        """
        <h3>Core equations and units</h3>
        <p>Use <strong>n = cV</strong>, where amount n is in mol, concentration c is in mol dm⁻³, and volume V is in dm³. Convert cm³ to dm³ by dividing by 1000.</p>
        <p>The structure is: calculate moles of the known solution → use the balanced equation's coefficient ratio → calculate the unknown amount → divide by the unknown volume in dm³ to find concentration.</p>
        <h3>Do not assume a 1:1 ratio</h3>
        <p>For 2NaOH + H₂SO₄ → Na₂SO₄ + 2H₂O, one mole of sulfuric acid reacts with two moles of sodium hydroxide.</p>
        <p>A measured ratio can also help infer an unknown hydroxide formula. If metal hydroxide:HCl is 1:2, this matches M(OH)₂ + 2HCl → MCl₂ + 2H₂O, under the assumptions of this reaction.</p>
        """,
        """
        <h4>Worked example from the master note</h4>
        <p>25.0 cm³ NaOH is neutralised by 15.10 cm³ of 0.200 mol dm⁻³ H₂SO₄.</p>
        <ol>
          <li>Convert acid volume: 15.10 / 1000 = 0.01510 dm³.</li>
          <li>n(H₂SO₄) = cV = 0.200 × 0.01510 = 0.003020 mol.</li>
          <li>Use the 1:2 acid:alkali ratio: n(NaOH) = 2 × 0.003020 = 0.006040 mol.</li>
          <li>Convert NaOH volume: 25.0 / 1000 = 0.0250 dm³.</li>
          <li>c = n/V = 0.006040 / 0.0250 = 0.2416 mol dm⁻³ ≈ 0.242 mol dm⁻³.</li>
        </ol>
        """,
        _open_question(
            "chem9701_l09_q", "25.0 cm³ of NaOH is exactly neutralised by 15.10 cm³ of 0.200 mol dm⁻³ H₂SO₄. Using 2NaOH + H₂SO₄ → Na₂SO₄ + 2H₂O, calculate the NaOH concentration. Show volume conversions, moles, mole ratio, and final units.",
            "15.10 cm³ = 0.01510 dm³; n(H₂SO₄) = 0.003020 mol; n(NaOH) = 0.006040 mol; 25.0 cm³ = 0.0250 dm³; c(NaOH) = 0.2416 ≈ 0.242 mol dm⁻³.",
            "Titration calculations", 6,
            [
                _point("acid_volume", "Converts 15.10 cm³ to 0.01510 dm³", numeric_targets=[{"value":0.01510,"tolerance":0.000005}]),
                _point("acid_moles", "Calculates 0.003020 mol H₂SO₄", numeric_targets=[{"value":0.003020,"tolerance":0.000005}]),
                _point("ratio", "Applies 1 mol H₂SO₄ : 2 mol NaOH", match_groups=[["1:2", "1 to 2", "twice", "multiply by 2"], ["h2so4"], ["naoh"]]),
                _point("alkali_moles", "Calculates 0.006040 mol NaOH", numeric_targets=[{"value":0.006040,"tolerance":0.00001}]),
                _point("alkali_volume", "Converts 25.0 cm³ to 0.0250 dm³", numeric_targets=[{"value":0.0250,"tolerance":0.00001}]),
                _point("concentration", "Calculates approximately 0.242 mol dm⁻³ NaOH", numeric_targets=[{"value":0.242,"tolerance":0.001}], match_any=["mol dm", "moldm", "mol/dm"]),
            ],
            answer="15.10 cm³ = 0.01510 dm³; n(H₂SO₄) = 0.003020 mol; acid:NaOH ratio = 1:2; n(NaOH) = 0.006040 mol; 25.0 cm³ = 0.0250 dm³; c(NaOH) = 0.2416 ≈ 0.242 mol dm⁻³.",
            typo_terms=["concentration", "titration", "sulfuric", "stoichiometry"],
        ),
    ),
    _lesson(
        10, "Limiting and Excess Reactants",
        """
        <h3>Find the reactant that runs out first</h3>
        <p>The limiting reactant determines the maximum amount of product. The excess reactant remains after the limiting reactant is used up. Do not compare masses directly: different substances have different molar masses and may have different coefficients.</p>
        <ol>
          <li>Write the balanced equation.</li>
          <li>Convert available mass, volume or concentration to moles.</li>
          <li>For each reactant, calculate available moles ÷ its coefficient.</li>
          <li>The smallest result identifies the limiting reactant; the others are in excess.</li>
          <li>Use the limiting reactant to calculate maximum product if asked.</li>
        </ol>
        """,
        """
        <h4>Worked example: sodium and sulfur</h4>
        <p>9.2 g Na reacts with 8.0 g S to form Na₂S: 2Na + S → Na₂S.</p>
        <ul>
          <li>n(Na) = 9.2 / 23 = 0.40 mol; compare 0.40 / 2 = 0.20.</li>
          <li>n(S) = 8.0 / 32 = 0.25 mol; compare 0.25 / 1 = 0.25.</li>
          <li>Sodium has the smaller coefficient-adjusted value, so Na is limiting and S is in excess.</li>
        </ul>
        <p>The smaller mass is not automatically limiting. Use moles and coefficients.</p>
        """,
        _open_question(
            "chem9701_l10_q", "9.2 g Na reacts with 8.0 g S according to 2Na + S → Na₂S. Calculate the moles of each reactant, compare moles divided by coefficients, and identify the limiting and excess reactants.",
            "n(Na) = 9.2/23 = 0.40 mol, then 0.40/2 = 0.20. n(S) = 8.0/32 = 0.25 mol, then 0.25/1 = 0.25. Sodium is limiting and sulfur is in excess.",
            "Limiting reactants", 5,
            [
                _point("na_moles", "Calculates 0.40 mol Na", numeric_targets=[{"value":0.40,"tolerance":0.01}]),
                _point("s_moles", "Calculates 0.25 mol S", numeric_targets=[{"value":0.25,"tolerance":0.01}]),
                _point("na_compare", "Divides sodium moles by coefficient 2 to get 0.20", numeric_targets=[{"value":0.20,"tolerance":0.01}]),
                _point("s_compare", "Divides sulfur moles by coefficient 1 to get 0.25", numeric_targets=[{"value":0.25,"tolerance":0.01}]),
                _point("identity", "Identifies sodium as limiting and sulfur as excess", match_groups=[["sodium", "na is", "na"], ["limiting"], ["sulfur", "s"], ["excess"]]),
            ],
            answer="Na: 0.40 mol; 0.40/2 = 0.20. S: 0.25 mol; 0.25/1 = 0.25. Sodium is limiting; sulfur is excess.",
        ),
    ),
    _lesson(
        11, "Gas-Volume Stoichiometry",
        """
        <h3>Using gas volume ratios</h3>
        <p>For gases measured at the same temperature and pressure, equal volumes contain equal numbers of molecules and therefore equal numbers of moles. Under those conditions, reacting gas volumes follow the coefficients in the balanced equation.</p>
        <ol>
          <li>Write and balance the equation.</li>
          <li>Confirm that the gas volumes are measured at the same temperature and pressure.</li>
          <li>Read the volume ratio from the coefficients.</li>
          <li>Use the ratio to calculate the unknown gas volume.</li>
        </ol>
        <p>Do not apply gas-volume ratios to solids or liquids. Volume ratio is not always mass ratio because mass depends on molar mass. Water can be gaseous in the stated reaction conditions; at room temperature it is normally liquid if condensed.</p>
        """,
        """
        <h4>Worked example: hydrogen and oxygen</h4>
        <p>2H₂(g) + O₂(g) → 2H₂O(g). The volume ratio H₂:O₂:H₂O(g) is 2:1:2.</p>
        <p>20 cm³ H₂ requires 10 cm³ O₂ when both gases are measured at the same temperature and pressure and react completely. The product label H₂O(g) applies only while water is gaseous; if condensed under ordinary room conditions, label it H₂O(l).</p>
        """,
        _open_question(
            "chem9701_l11_q", "Hydrogen reacts with oxygen: 2H₂(g) + O₂(g) → 2H₂O(g). Calculate the oxygen volume required for 20 cm³ of hydrogen at the same temperature and pressure. State the volume ratio and explain why it cannot be used as a mass ratio.",
            "The coefficient ratio H₂:O₂:H₂O(g) is 2:1:2. 20 cm³ H₂ requires 10 cm³ O₂. Gas volume tracks mole ratio at the same temperature and pressure; mass depends on molar mass.",
            "Gas-volume ratios", 4,
            [
                _point("ratio", "States the H₂:O₂ ratio is 2:1", match_any=["2:1", "2 to 1"]),
                _point("volume", "Calculates 10 cm³ O₂", numeric_targets=[{"value":10,"tolerance":0.01}], match_any=["cm3", "cm³"]),
                _point("conditions", "Mentions same temperature and pressure", match_groups=[["temperature"], ["pressure"], ["same"]]),
                _point("mass", "Explains mass depends on molar mass and is not given by the gas-volume ratio", match_groups=[["mass"], ["molar mass", "masses differ"], ["not", "different"]]),
            ],
            answer="10 cm³ oxygen; H₂:O₂ = 2:1 at the same temperature and pressure. The volume ratio is not the mass ratio because molar masses differ.",
        ),
    ),
    _lesson(
        12, "Exam Traps and the Universal Self-Check",
        """
        <h3>Common errors and prevention rules</h3>
        <ul>
          <li>Do not use Greek prefixes for ionic compounds: classify the compound first.</li>
          <li>A Roman numeral is the oxidation state of a variable-charge metal, not an atom count.</li>
          <li>Write Ca(OH)₂, not CaOH₂, when two complete hydroxide ions are present.</li>
          <li>Keep polyatomic-ion charges and subscripts correct.</li>
          <li>Balance with coefficients; changing subscripts changes the substance.</li>
          <li>(aq) means dissolved in water; (l) means pure liquid.</li>
          <li>Do not split solids into ions. Split only soluble aqueous strong electrolytes under the course convention.</li>
          <li>Cancel only identical spectator ions on both sides.</li>
          <li>Never assume a 1:1 titration ratio; use the balanced equation.</li>
          <li>For limiting reactants, convert to moles and divide by coefficients; do not compare grams directly.</li>
          <li>Apply gas-volume ratios only to gases at the same temperature and pressure.</li>
        </ul>
        <h3>Universal equation workflow</h3>
        <p>Read the sentence → identify reactants and products → write correct formulae → balance coefficients → add state symbols → split eligible aqueous electrolytes if ionic form is requested → cancel spectators → check atoms and total charge.</p>
        <h3>Name ↔ formula workflow</h3>
        <p>Classify the compound → identify ions/charges or molecular prefixes → balance ionic charge → use brackets for repeated polyatomic groups → check atom count and charge. In the reverse direction, calculate variable metal charge from neutrality and use the correct naming system.</p>
        """,
        """
        <h4>Final self-check before submitting</h4>
        <ol>
          <li>Correct formula/name, including Roman numerals and polyatomic subscripts?</li>
          <li>Does each ionic formula have zero total charge?</li>
          <li>Were atoms balanced with coefficients only?</li>
          <li>Are states consistent with the problem and solubility rules?</li>
          <li>Were solids, liquids and gases kept intact in the ionic equation?</li>
          <li>Were only identical ions cancelled?</li>
          <li>For titration, were cm³ converted to dm³ and coefficients used?</li>
          <li>For limiting reactants, were moles divided by coefficients?</li>
          <li>For gas volumes, are the gases at the same temperature and pressure?</li>
        </ol>
        <p>Identity first; conservation second; physical states third; reacting particles fourth; quantities last.</p>
        """,
        _open_question(
            "chem9701_l12_q", "A learner writes CaOH₂ for calcium hydroxide, changes a subscript to balance an equation, labels dissolved NaCl as (l), and cancels K⁺ from only one side of an ionic equation. Identify and correct all four errors, then give the universal workflow for equation questions.",
            "Correct formula: Ca(OH)₂. Change coefficients, not subscripts. NaCl dissolved in water is NaCl(aq). Cancel spectator ions only when identical on both sides. Workflow: names to formulae, balance, state symbols, split eligible aqueous electrolytes, cancel spectators, audit atoms and charge.",
            "Exam error diagnosis", 6,
            [
                _point("formula", "Corrects CaOH₂ to Ca(OH)₂ and explains repeated OH⁻ group", match_groups=[["ca(oh)2"], ["bracket", "two hydroxide", "oh group"]]),
                _point("balance", "States coefficients change, not subscripts", match_groups=[["coefficient"], ["not subscripts", "never change subscripts", "subscripts unchanged"]]),
                _point("state", "Corrects dissolved NaCl to NaCl(aq)", match_any=["nacl(aq)", "nacl (aq)", "aqueous"]),
                _point("cancel", "Cancels K⁺ only if identical on both sides and explains why", match_groups=[["k+"], ["both sides"], ["identical", "same"], ["spectator", "unchanged"]]),
                _point("sequence1", "Places correct formulae before balancing", match_groups=[["formula"], ["before", "first"], ["balance"]]),
                _point("sequence2", "Includes states, splitting, cancellation and final atom/charge check", match_groups=[["state"], ["aqueous", "split", "ions"], ["cancel"], ["atom"], ["charge"]]),
            ],
            answer="Ca(OH)₂ is correct because the two hydroxide ions need brackets. Write correct formulae first, then change coefficients only; never change subscripts. Dissolved NaCl is NaCl(aq). Cancel K⁺ only if identical on both sides. Add states, split eligible aqueous electrolytes, keep solids, liquids, gases and water intact, cancel spectators, then check atoms and charge.",
            typo_terms=["coefficient", "subscript", "aqueous", "spectator"],
        ),
        kind="application",
    ),
]


# Screen 3 is a short practice set, not just a single item. These additional
# open-ended questions stay within the course skills and use the same rubric
# format as the main question. Each lesson keeps its main question first.
_EXTRA_PRACTICE = {
    1: [
        _open_question("chem9701_l01_q2",
            "Expand 3Ca(OH)₂ and state the total numbers of Ca, O, and H atoms.",
            "The coefficient multiplies the entire formula, so Ca = 3, O = 6, and H = 6.",
            "Formula notation", 3, [
                _point("ca", "States Ca = 3", regex_any=[r"(?:^|[^a-z])ca(?:=|:|is)3(?:[^0-9]|$)"]),
                _point("o", "States O = 6", regex_any=[r"(?:^|[^a-z])o(?:=|:|is)6(?:[^0-9]|$)"]),
                _point("h", "States H = 6", regex_any=[r"(?:^|[^a-z])h(?:=|:|is)6(?:[^0-9]|$)"]),
            ], answer="Ca = 3, O = 6, H = 6."),
        _open_question("chem9701_l01_q3",
            "Show why Al₂O₃ is electrically neutral when aluminium ions are Al³⁺ and oxide ions are O²⁻.",
            "Two Al³⁺ ions contribute +6 and three O²⁻ ions contribute −6, giving total charge zero.",
            "Ionic charge", 2, [
                _point("positive", "Calculates total positive charge as +6", match_groups=[["2al", "two al", "two aluminium"], ["+6", "positive 6", "2(+3)", "2*3"]]),
                _point("negative", "Calculates total negative charge as −6 and concludes neutrality", match_groups=[["-6", "negative 6", "3(-2)", "3*(-2)"], ["zero", "neutral", "balances"]]),
            ], answer="2(+3) + 3(−2) = +6 − 6 = 0."),
    ],
    2: [
        _open_question("chem9701_l02_q2",
            "Name PbO₂ and CuBr. Show how charge balance determines the Roman numeral in each name.",
            "PbO₂ is lead(IV) oxide because two O²⁻ ions total −4. CuBr is copper(I) bromide because Br⁻ is −1.",
            "Compound naming", 4, [
                _point("lead", "Names PbO₂ lead(IV) oxide", match_any=["lead(iv)oxide", "lead(4)oxide", "leadiv oxide"]),
                _point("copper", "Names CuBr copper(I) bromide", match_any=["copper(i)bromide", "copper(1)bromide", "copperi bromide"]),
                _point("lead_charge", "Uses two oxide ions to deduce Pb is +4", match_groups=[["two oxygen", "2o", "two oxide"], ["-4", "negative four"], ["+4", "lead(iv)", "lead is 4"]]),
                _point("copper_charge", "Uses bromide −1 to deduce Cu is +1", match_groups=[["bromide"], ["-1", "negative one"], ["+1", "copper(i)", "copper is 1"]]),
            ], answer="PbO₂ is lead(IV) oxide because two O²⁻ ions total −4, so Pb is +4. CuBr is copper(I) bromide because Br⁻ is −1, so Cu is +1."),
        _open_question("chem9701_l02_q3",
            "Name SF₆, N₂O₅, and PBr₅. Explain what the prefixes tell you.",
            "Sulfur hexafluoride; dinitrogen pentoxide; phosphorus pentabromide. Prefixes state atom counts in molecular compounds.",
            "Molecular prefixes", 4, [
                _point("sf6", "Names SF₆ sulfur hexafluoride", match_any=["sulfur hexafluoride", "sulphur hexafluoride"]),
                _point("n2o5", "Names N₂O₅ dinitrogen pentoxide", match_any=["dinitrogen pentoxide"]),
                _point("pbr5", "Names PBr₅ phosphorus pentabromide", match_any=["phosphorus pentabromide"]),
                _point("prefix", "Explains prefixes state atom counts in molecular compounds", match_groups=[["prefix"], ["number", "count", "how many"], ["atom"]]),
            ], answer="Sulfur hexafluoride; dinitrogen pentoxide; phosphorus pentabromide. The prefixes give atom counts in these molecular compounds."),
    ],
    3: [
        _open_question("chem9701_l03_q2",
            "Write the formulae for magnesium nitrate and ammonium phosphate. Explain the charge ratios.",
            "Mg(NO₃)₂ balances Mg²⁺ with two NO₃⁻ ions. (NH₄)₃PO₄ balances three NH₄⁺ with PO₄³⁻.",
            "Polyatomic ions and formulae", 4, [
                _point("mg", "Writes Mg(NO₃)₂", match_any=["mg(no3)2"]),
                _point("ammonium", "Writes (NH₄)₃PO₄", match_any=["(nh4)3po4"]),
                _point("mg_charge", "Explains +2 magnesium requires two −1 nitrates", match_groups=[["mg2+", "magnesium +2", "magnesium is +2"], ["two nitrate", "2no3", "two no3"], ["-1", "negative one"]]),
                _point("ammonium_charge", "Explains three +1 ammonium ions balance −3 phosphate", match_groups=[["three ammonium", "3nh4"], ["+1", "positive one"], ["po4", "phosphate"], ["-3", "negative three", "neutral", "zero"]]),
            ], answer="Mg(NO₃)₂ because Mg²⁺ is balanced by two NO₃⁻ ions; (NH₄)₃PO₄ because three NH₄⁺ ions balance PO₄³⁻."),
        _open_question("chem9701_l03_q3",
            "Distinguish nitrate from nitrite and sulfate from sulfite by formula and oxygen count.",
            "Nitrate NO₃⁻ versus nitrite NO₂⁻; sulfate SO₄²⁻ versus sulfite SO₃²⁻. In each pair the -ite ion has one fewer oxygen.",
            "Polyatomic ions", 4, [
                _point("nitrate", "Writes NO₃⁻ for nitrate", match_any=["no3-","no3⁻"]),
                _point("nitrite", "Writes NO₂⁻ for nitrite", match_any=["no2-","no2⁻"]),
                _point("sulfate", "Writes SO₄²⁻ for sulfate", match_any=["so42-","so₄²⁻","so4^2-"]),
                _point("oxygen", "States the -ite member has one fewer oxygen in both pairs", match_groups=[["-ite", "ite"], ["one fewer", "one less", "fewer oxygen"], ["oxygen"]]),
            ], answer="Nitrate NO₃⁻, nitrite NO₂⁻; sulfate SO₄²⁻, sulfite SO₃²⁻; -ite has one fewer O."),
    ],
    4: [
        _open_question("chem9701_l04_q2",
            "Name HNO₃ and HNO₂, then explain the suffix change using the names nitrate and nitrite.",
            "HNO₃ is nitric acid from nitrate; HNO₂ is nitrous acid from nitrite. -ate becomes -ic and -ite becomes -ous.",
            "Acid nomenclature", 3, [
                _point("nitric", "Names HNO₃ nitric acid", match_any=["nitric acid"]),
                _point("nitrous", "Names HNO₂ nitrous acid", match_any=["nitrous acid"]),
                _point("suffix", "Explains -ate → -ic and -ite → -ous", match_groups=[["ate"], ["ic"], ["ite"], ["ous"]]),
            ], answer="HNO₃ nitric acid; HNO₂ nitrous acid. -ate becomes -ic; -ite becomes -ous.",
            typo_terms=["nitric", "nitrous"]),
        _open_question("chem9701_l04_q3",
            "Distinguish HBr(g) from HBr(aq) and state the binary-acid naming rule.",
            "HBr(g) is hydrogen bromide gas; HBr(aq) is hydrobromic acid. For an oxygen-free acid in aqueous solution, use hydro- + anion root + -ic acid.",
            "Acid nomenclature", 3, [
                _point("gas", "Identifies HBr(g) as hydrogen bromide gas", match_groups=[["hydrogen bromide"], ["gas", "(g)"]]),
                _point("aqueous", "Identifies HBr(aq) as hydrobromic acid", match_any=["hydrobromic acid"]),
                _point("rule", "States hydro- + root + -ic acid for a binary acid", match_groups=[["hydro"], ["root"], ["ic acid", "-ic"]]),
            ], answer="HBr(g) is hydrogen bromide gas; HBr(aq) is hydrobromic acid. For an oxygen-free acid in water, use hydro- + anion root + -ic acid."),
    ],
    5: [
        _open_question("chem9701_l05_q2",
            "Write the formulae for copper(I) oxide and copper(II) oxide. Explain why the formulae differ.",
            "Copper(I) oxide is Cu₂O; copper(II) oxide is CuO. O²⁻ needs two Cu⁺ ions but only one Cu²⁺ ion.",
            "Name–formula translation", 3, [
                _point("cu1", "Writes Cu₂O for copper(I) oxide", match_any=["cu2o"]),
                _point("cu2", "Writes CuO for copper(II) oxide", match_any=["cuo"]),
                _point("ratio", "Explains metal charge changes the neutral ratio with O²⁻", match_groups=[["cu+", "copper(i)", "copper one"], ["cu2+", "copper(ii)", "copper two"], ["o2-", "oxide"], ["ratio", "two copper", "1:2", "two cu"]]),
            ], answer="Copper(I) oxide is Cu₂O; copper(II) oxide is CuO. Cu⁺ requires two copper ions to balance O²⁻, whereas Cu²⁺ balances oxide 1:1."),
        _open_question("chem9701_l05_q3",
            "Write the formula for dinitrogen pentoxide and name FeCl₂. Explain how prefixes differ from Roman numerals.",
            "Dinitrogen pentoxide is N₂O₅; FeCl₂ is iron(II) chloride. Prefixes give atom counts in molecular compounds; Roman numerals give a variable-charge metal's oxidation state.",
            "Name–formula translation", 4, [
                _point("n2o5", "Writes N₂O₅", match_any=["n2o5"]),
                _point("iron", "Names FeCl₂ iron(II) chloride", match_any=["iron(ii)chloride", "iron(2)chloride"]),
                _point("prefix", "Says prefixes describe atom counts in molecular compounds", match_groups=[["prefix"], ["atom count", "number of atoms", "how many atoms"], ["molecular"]]),
                _point("roman", "Says Roman numerals describe metal oxidation state/charge", match_groups=[["roman numeral"], ["oxidation state", "charge"], ["metal"]]),
            ], answer="Dinitrogen pentoxide is N₂O₅; FeCl₂ is iron(II) chloride. Prefixes count atoms in molecular compounds; Roman numerals give a variable-charge metal oxidation state, not atom count."),
    ],
    6: [
        _open_question("chem9701_l06_q2",
            "Balance the complete combustion of hexane: C₆H₁₄ + O₂ → CO₂ + H₂O. State the order you used.",
            "2C₆H₁₄ + 19O₂ → 12CO₂ + 14H₂O. A useful method is to balance C, then H, then O.",
            "Equation balancing", 4, [
                _point("equation", "Gives coefficients 2, 19, 12, 14", match_any=["2c6h14+19o2->12co2+14h2o", "2c6h14+19o2→12co2+14h2o"]),
                _point("carbon", "Balances 12 carbon atoms", match_groups=[["carbon", "c"], ["12"]]),
                _point("hydrogen", "Balances 28 hydrogen atoms", match_groups=[["hydrogen", "h"], ["28"]]),
                _point("order", "Describes balancing C, then H, then O", match_groups=[["c", "carbon"], ["h", "hydrogen"], ["o", "oxygen"]]),
            ], answer="2C₆H₁₄ + 19O₂ → 12CO₂ + 14H₂O. There are 12 carbon atoms and 28 hydrogen atoms on each side; a useful order is C, then H, then O."),
        _open_question("chem9701_l06_q3",
            "Balance  Al(OH)₃ → Al₂O₃ + H₂O and explain why you must not change any formula subscripts.",
            "2Al(OH)₃ → Al₂O₃ + 3H₂O. Coefficients balance atom counts without changing substance identity.",
            "Equation balancing", 2, [
                _point("equation", "Gives 2Al(OH)₃ → Al₂O₃ + 3H₂O", match_any=["2al(oh)3->al2o3+3h2o", "2al(oh)3→al2o3+3h2o"]),
                _point("rule", "Explains coefficients change but subscripts define substances", match_groups=[["coefficient"], ["not subscripts", "subscripts unchanged"], ["substance", "identity", "formula"]]),
            ], answer="2Al(OH)₃ → Al₂O₃ + 3H₂O. Change coefficients only; subscripts define the substances."),
    ],
    7: [
        _open_question("chem9701_l07_q2",
            "State two solubility patterns from the course and give one relevant exception.",
            "Examples: all nitrates are soluble; Group 1 and ammonium salts are soluble; most halides are soluble with AgCl and PbCl₂ as exceptions; BaSO₄ and PbSO₄ are insoluble.",
            "Solubility", 3, [
                _point("pattern1", "States one correct general solubility pattern", match_any=["all nitrates soluble", "nitrates are soluble", "group 1", "ammonium salts soluble", "most chlorides", "most sulfates"]),
                _point("pattern2", "States a second valid pattern", match_any=["all nitrates soluble", "nitrates are soluble", "group 1", "ammonium salts soluble", "most chlorides", "most sulfates", "most carbonates", "most phosphates"]),
                _point("exception", "Gives a source-listed exception", match_any=["agcl", "pbcl2", "baso4", "pbso4", "caso4"]),
            ], answer="All nitrates are soluble; Group 1 and ammonium salts are soluble; most chlorides are soluble except AgCl and PbCl₂; BaSO₄ is insoluble."),
        _open_question("chem9701_l07_q3",
            "Add state symbols to CaCO₃ + HCl → CaCl₂ + H₂O + CO₂ and explain why the products have those states.",
            "CaCO₃(s) + 2HCl(aq) → CaCl₂(aq) + H₂O(l) + CO₂(g). The carbonate is solid, solutions are aqueous, water is liquid, and carbon dioxide is gas.",
            "State symbols", 4, [
                _point("equation", "Writes balanced equation with state symbols", match_any=["caco3(s)+2hcl(aq)->cacl2(aq)+h2o(l)+co2(g)", "caco3(s)+2hcl(aq)→cacl2(aq)+h2o(l)+co2(g)"]),
                _point("solid", "Identifies CaCO₃ as a solid", match_any=["caco3(s)"]),
                _point("aqueous", "Identifies HCl and CaCl₂ as aqueous", match_groups=[["hcl(aq)"], ["cacl2(aq)"]]),
                _point("products", "Identifies liquid water and gaseous carbon dioxide", match_groups=[["h2o(l)"], ["co2(g)"]]),
            ], answer="CaCO₃(s) + 2HCl(aq) → CaCl₂(aq) + H₂O(l) + CO₂(g). CaCO₃ is solid; HCl and CaCl₂ are aqueous; water is liquid; CO₂ is gas."),
    ],
    8: [
        _open_question("chem9701_l08_q2",
            "Write the net ionic equation for zinc displacing copper from aqueous copper(II) sulfate. Identify the spectator ion.",
            "Zn(s) + Cu²⁺(aq) → Zn²⁺(aq) + Cu(s). Sulfate, SO₄²⁻, is the spectator ion.",
            "Ionic equations", 2, [
                _point("net", "Writes Zn + Cu²⁺ → Zn²⁺ + Cu", match_any=["zn(s)+cu2+(aq)->zn2+(aq)+cu(s)", "zn+cu2+->zn2++cu"]),
                _point("spectator", "Identifies sulfate as the spectator ion", match_groups=[["sulfate", "so4"], ["spectator", "unchanged"]]),
            ], answer="Zn(s) + Cu²⁺(aq) → Zn²⁺(aq) + Cu(s); sulfate is spectator."),
        _open_question("chem9701_l08_q3",
            "Write the net ionic equation for HCl(aq) + NaOH(aq) → NaCl(aq) + H₂O(l). Explain which ions cancel.",
            "H⁺(aq) + OH⁻(aq) → H₂O(l). Na⁺ and Cl⁻ are spectator ions and cancel.",
            "Ionic equations", 3, [
                _point("net", "Writes H⁺ + OH⁻ → H₂O", match_any=["h++oh-->h2o", "h+(aq)+oh-(aq)->h2o(l)"]),
                _point("sodium", "Identifies Na⁺ as spectator", match_any=["na+"]),
                _point("chloride", "Identifies Cl⁻ as spectator and explains cancellation", match_groups=[["cl-"], ["spectator", "cancel", "unchanged"]]),
            ], answer="H⁺(aq) + OH⁻(aq) → H₂O(l); Na⁺ and Cl⁻ cancel."),
    ],
    9: [
        _open_question("chem9701_l09_q2",
            "A metal hydroxide sample of 25.0 cm³ at 0.0500 mol dm⁻³ is neutralised by 12.50 cm³ of 0.200 mol dm⁻³ HCl. Calculate both amounts in moles and deduce the hydroxide pattern.",
            "n(hydroxide) = 0.0500 × 0.0250 = 1.25×10⁻³ mol. n(HCl) = 0.200 × 0.01250 = 2.50×10⁻³ mol. Ratio hydroxide:HCl = 1:2, consistent with M(OH)₂ + 2HCl → MCl₂ + 2H₂O.",
            "Titration stoichiometry", 3, [
                _point("hydroxide_moles", "Calculates 1.25×10⁻³ mol hydroxide", numeric_targets=[{"value":0.00125,"tolerance":0.00001}]),
                _point("acid_moles", "Calculates 2.50×10⁻³ mol HCl", numeric_targets=[{"value":0.00250,"tolerance":0.00001}]),
                _point("ratio", "Deduces 1:2 ratio and M(OH)₂ pattern", match_groups=[["1:2", "1 to 2", "twice"], ["m(oh)2", "two oh", "two hydroxide"]]),
            ], answer="n(hydroxide)=1.25×10⁻³ mol; n(HCl)=2.50×10⁻³ mol; ratio 1:2, so M(OH)₂."),
        _open_question("chem9701_l09_q3",
            "Explain the sequence for finding an unknown concentration in a titration. Include the unit conversion and balanced-equation ratio.",
            "Convert cm³ to dm³; use n=cV for known solution moles; use the balanced equation coefficient ratio to find unknown moles; calculate c=n/V using the unknown volume in dm³.",
            "Titration method", 3, [
                _point("convert", "Converts cm³ to dm³ by dividing by 1000", match_groups=[["cm3", "cm³"], ["dm3", "dm³"], ["1000"]]),
                _point("moles", "Uses n = cV for known-solution moles", match_groups=[["n=cv", "c*v", "concentration"], ["moles", "amount"]]),
                _point("ratio", "Uses coefficient ratio then c = n/V", match_groups=[["balanced equation", "coefficient ratio", "mole ratio"], ["c=n/v", "n/v", "concentration"]]),
            ], answer="Convert cm³ to dm³ by dividing by 1000, calculate known moles with n=cV, apply the balanced-equation mole ratio, then calculate c=n/V using the unknown volume in dm³."),
    ],
    10: [
        _open_question("chem9701_l10_q2",
            "Using 2Na + S → Na₂S, the available quantities give 0.40 mol Na and 0.25 mol S. Calculate each divided by its coefficient and the maximum Na₂S amount.",
            "Na: 0.40/2 = 0.20. S: 0.25/1 = 0.25. Sodium is limiting, so the maximum Na₂S amount is 0.20 mol.",
            "Limiting reactants", 3, [
                _point("na", "Calculates 0.20 for sodium after dividing by 2", numeric_targets=[{"value":0.20,"tolerance":0.01}]),
                _point("s", "Calculates 0.25 for sulfur after dividing by 1", numeric_targets=[{"value":0.25,"tolerance":0.01}]),
                _point("product", "Identifies sodium as limiting and 0.20 mol Na₂S as maximum", match_groups=[["sodium", "na"], ["limiting"], ["0.20", "0.2"], ["na2s", "sodium sulfide"]]),
            ], answer="Na: 0.40 mol; 0.40/2 = 0.20. S: 0.25 mol; 0.25/1 = 0.25. Sodium is the limiting reactant and can produce at most 0.20 mol Na₂S."),
        _open_question("chem9701_l10_q3",
            "Why is comparing the masses 9.2 g Na and 8.0 g S not enough to identify the limiting reactant? State the correct method.",
            "Molar masses and coefficient requirements differ. Convert each reactant to moles, divide each mole amount by its balanced-equation coefficient, and select the smallest result.",
            "Limiting-reactant reasoning", 2, [
                _point("why", "Explains that substances have different molar masses and/or coefficients", match_groups=[["molar mass", "molar masses"], ["different", "coefficient", "ratio"]]),
                _point("method", "Says convert to moles then divide by coefficient and choose smallest", match_groups=[["moles"], ["divide", "divided"], ["coefficient"], ["smallest"]]),
            ], answer="Mass alone ignores different molar masses and coefficient ratios. Convert to moles, divide by coefficients, choose the smallest."),
    ],
    11: [
        _open_question("chem9701_l11_q2",
            "For 2H₂(g) + O₂(g) → 2H₂O(g), calculate the oxygen volume required for 60 cm³ H₂ at the same temperature and pressure.",
            "The H₂:O₂ volume ratio is 2:1, so 60 cm³ H₂ needs 30 cm³ O₂.",
            "Gas-volume ratios", 2, [
                _point("ratio", "Uses H₂:O₂ = 2:1", match_any=["2:1", "2 to 1"]),
                _point("volume", "Calculates 30 cm³ oxygen", numeric_targets=[{"value":30,"tolerance":0.01}], match_any=["cm3", "cm³"]),
            ], answer="30 cm³ O₂."),
        _open_question("chem9701_l11_q3",
            "A learner says the equation coefficient ratio is also the mass ratio. Explain why this is incorrect and state the conditions required for gas-volume ratios.",
            "Coefficients give mole ratios. Gas volumes follow those ratios only for gases at the same temperature and pressure; masses depend on molar masses.",
            "Gas-volume reasoning", 3, [
                _point("coefficients", "States coefficients give mole ratios", match_groups=[["coefficient"], ["mole ratio", "moles"]]),
                _point("conditions", "States gases must be at the same temperature and pressure", match_groups=[["gas"], ["same"], ["temperature"], ["pressure"]]),
                _point("mass", "Explains mass depends on molar mass", match_groups=[["mass"], ["molar mass"]]),
            ], answer="Coefficient ratios are mole ratios; gas volumes follow at same temperature and pressure; mass depends on molar mass."),
    ],
    12: [
        _open_question("chem9701_l12_q2",
            "Give the full workflow for a word-equation question that asks for a balanced net ionic equation with state symbols.",
            "Identify reactants/products; write correct formulae; balance coefficients; add states; split soluble aqueous strong electrolytes; keep solids/liquids/gases/water intact; cancel identical spectator ions; check atoms and charge.",
            "Exam workflow", 4, [
                _point("identity", "Writes correct formulae before balancing", match_groups=[["formula"], ["before", "first"], ["balance"]]),
                _point("balance_states", "Balances with coefficients and adds state symbols", match_groups=[["coefficient", "balance"], ["state symbol", "states"]]),
                _point("ions", "Splits only soluble aqueous strong electrolytes and retains other states intact", match_groups=[["aqueous", "aq"], ["split", "ions"], ["solid", "liquid", "gas", "water"]]),
                _point("audit", "Cancels identical spectator ions then checks atoms and charge", match_groups=[["spectator"], ["cancel"], ["atom"], ["charge"]]),
            ], answer="Write correct formulae first, then balance with coefficients; add state symbols, split eligible aqueous electrolytes, keep solids, liquids, gases and water intact, cancel spectators, then check atoms and charge."),
        _open_question("chem9701_l12_q3",
            "A learner cancels SO₄²⁻(aq) on the left against SO₄²⁻(s) on the right. Explain why this is invalid and state the spectator-ion test.",
            "They differ in state, so they are not identical species. A spectator ion must have the same formula, charge, and state on both sides and remain unchanged.",
            "Spectator-ion error diagnosis", 3, [
                _point("state", "Explains aqueous and solid sulfate are different states", match_groups=[["aq", "aqueous"], ["solid", "(s)"], ["different", "not identical"]]),
                _point("formula_charge_state", "Requires same formula, charge and state on both sides", match_groups=[["formula"], ["charge"], ["state"], ["both sides"]]),
                _point("unchanged", "States a spectator ion is unchanged", match_any=["unchanged", "does not change", "no change"]),
            ], answer="Invalid because aqueous and solid sulfate differ in state. A spectator ion must have the same formula, charge and state on both sides and remains unchanged."),
    ],
}

for _lesson_record in LESSONS:
    _bank = [_lesson_record["interactive_question"]] + _EXTRA_PRACTICE[int(_lesson_record["id"].split("l")[-1])]
    _lesson_record["practice_questions"] = _bank
    _lesson_record["questions"] = _bank


CHEMISTRY_COURSE = {
    "id": "chemistry_9701",
    "title": "Chemical Formulae and Equations",
    "short_description": (
        "A complete Grade 10 course on nomenclature, formula writing, "
        "balanced equations, state symbols, ionic reactions, and stoichiometry."
    ),
    "difficulty": "Intermediate",
    "topic_label": "Chemistry 9701",
    "category_id": "academics",
    "subject_id": "chemistry",
    "level": "Grade 10",
    "curriculum": "Cambridge International AS & A Level Chemistry 9701",
    "course_version": "1.0.0",
    "lessons": LESSONS,
}

__all__ = ["CHEMISTRY_COURSE", "LESSONS", "COURSE_DIAGNOSTIC"]
