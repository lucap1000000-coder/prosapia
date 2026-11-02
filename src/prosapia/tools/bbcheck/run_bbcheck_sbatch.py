from prosapia.core import ManifestCtx


def build_bbcheck_manifest(ctx: ManifestCtx):
    rows = []
    for name, row in ctx.ready.iterrows():
        rows.append((name, str(row[ctx.args.input_column])))
    return rows
