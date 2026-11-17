from prosapia.core import ManifestCtx

def build_c12_clash_manifest(ctx: ManifestCtx):
    rows = []
    for name, row in ctx.ready.iterrows():
        rows.append((name, str(row[ctx.args.input_column])))
    return rows
