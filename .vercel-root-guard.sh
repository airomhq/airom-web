#!/usr/bin/env bash
# Fails any Vercel build whose Root Directory is the repository root.
#
# Nothing is deployable from here. This repo holds two independent sites —
# www/ (airom.dev) and docs-site/ (docs.airom.dev) — each with its own
# vercel.json. Vercel reads vercel.json from the project's Root Directory, so
# THIS file is only ever reached when a project is misconfigured to build from
# the root, and is invisible in the correct configuration.
#
# Why it is worth a guard rather than a comment: with Root Directory "." the
# landing project's Output Directory "." resolves to the whole repository, and
# Vercel would happily publish it — docs-site sources, .github/, README and all
# — at airom.dev. That is a green build serving the wrong thing, which is the
# failure mode nobody notices. Better a red build with instructions.
#
# CLI deploys (`vercel deploy` run from inside www/ or docs-site/) upload only
# that folder, so "." means the right thing there and this never fires. The
# misconfiguration only becomes reachable once the projects are connected to
# Git and Vercel starts cloning the entire repository.
echo "" >&2
echo "  This repository cannot be built from its root." >&2
echo "" >&2
echo "  Set the project's Root Directory in Vercel:" >&2
echo "    Settings -> Build and Deployment -> Root Directory" >&2
echo "" >&2
echo "      airom-www   ->  www          (serves airom.dev)" >&2
echo "      airom-docs  ->  docs-site    (serves docs.airom.dev)" >&2
echo "" >&2
echo "  Each directory carries its own vercel.json with the correct build" >&2
echo "  command, output directory and headers." >&2
echo "" >&2
exit 1
