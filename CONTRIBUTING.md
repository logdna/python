# Contributing

## Process

We use a fork-and-PR process, also known as a triangular workflow. This process
is fairly common in open-source projects. Here's the basic workflow:

1. Fork the upstream repo to create your own repo. This repo is called the origin repo.
2. Clone the origin repo to create a working directory on your local machine. 
3. Work your changes on a branch in your working directory, then add, commit, and push your work to your origin repo.
4. Submit your changes as a PR against the upstream repo. You can use the upstream repo UI to do this.
5. Maintainers review your changes. If they ask for changes, you work on your
   origin repo's branch and then submit another PR. Otherwise, if no changes are made, 
   then the branch with your PR is merged to upstream's main trunk, the master branch.

When you work in a triangular workflow, you have the upstream repo, the origin
repo, and then your working directory (the clone of the origin repo). You do 
a `git fetch` from upstream to local, push from local to origin, and then do a PR from origin to
upstream&mdash;a triangle.

If this workflow is too much to understand to start, that's ok! You can use
GitHub's UI to make a change, which is autoset to do most of this process for
you. We just want you to be aware of how the entire process works before
proposing a change.

Thank you for your contributions; we appreciate you!

## License

Note that we use a standard [MIT](./LICENSE) license on this repo.

## Coding style

Currently the project is auto formatted following the [PEP8][]
style guide

[PEP8]: https://www.python.org/dev/peps/pep-0008
