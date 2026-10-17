# Third-party dependency notices

The offline runtime bundles the following unmodified Python wheels. Their
complete licence texts are included in `third_party_licenses/`.

| Package | Version | Licence |
|---|---:|---|
| NetworkX | 3.4.2 | BSD 3-Clause |
| decorator | 5.2.1 | BSD 2-Clause |

These dependencies are used only to implement deterministic weighted general
graph matching and its Python runtime support. The wheel files are retained in
`wheelhouse/` so the image can be built without network access.