Plugin for CudaText.
Plugin gives command "Sum Lines", which sums numbers in selection. 
Supported normal/column selections. 
Multi-selections not yet supported.

Empty/spaces lines are ignored.
Float numbers (with dot) are supported.
It shows report in a new tab.

Example of selected text:

    10
    100.10
    dd
    20.005
    100.10d

Report will be like:

    Normal selection: lines 10..14

    Sum: 130.105
    Min: 10.0
    Max: 100.1
    Avg: 43.36833333333333
    Numbers processed: 3
    Lines processed: 5
    Lines skipped: 2
      - selection line 3:     dd
      - selection line 5:     100.10d


Author: Alexey (CudaText)
License: MIT
