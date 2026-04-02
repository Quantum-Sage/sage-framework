import os

intro_path = r'C:\Users\tylor\Desktop\the apex signel\SAGE-Framework\papers\paper1_introduction_v2.md'
sec23_path = r'C:\Users\tylor\.gemini\antigravity\brain\7af630e1-dd89-4b55-b5ab-af45c9a05e3b\paper1_sections_2_and_3.md'
sec410_path = r'C:\Users\tylor\.gemini\antigravity\brain\7af630e1-dd89-4b55-b5ab-af45c9a05e3b\paper1_sections_4_to_10.md'
output_path = r'C:\Users\tylor\Desktop\the apex signel\SAGE-Framework\papers\SAGE_No_Cloning_Gap_Complete_Manuscript.md'

with open(intro_path, 'r', encoding='utf-8') as f:
    intro_txt = f.read()

parts = intro_txt.split('## References')
intro_main = parts[0].strip()
refs = '## References\n' + parts[1].strip()

with open(sec23_path, 'r', encoding='utf-8') as f:
    sec23_txt = f.read()

with open(sec410_path, 'r', encoding='utf-8') as f:
    sec410_txt = f.read()

combined = f"{intro_main}\n\n{sec23_txt}\n\n{sec410_txt}\n\n{refs}"

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(combined)

print('Success: ' + output_path)
