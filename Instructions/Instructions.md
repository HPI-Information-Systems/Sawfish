# Reproducibility Instructions for Discovering Similarity Inclusion Dependencies

The source code and the artifacts required to reproduce the results of the paper “Discovering Similarity Inclusion Dependencies” [1] can be found at the link <https://github.com/HPI-Information-Systems/Sawfish>.

---

## 1. Prerequisites

First, clone the repository on your machine by running:
`git clone https://github.com/HPI-Information-Systems/Sawfish.git`

---

## 2. Execution

We provide docker containers that run the sawfish script – therefore one system requirement is the use of docker and docker-compose. If you wish to manually install all the requirements and adjust settings, please follow the Manual Installation instructions below. <span style="color:red">Otherwise, continue reading</span>.

### Docker Usage

If you chose to use docker for reproduction, a system requirement is docker and docker compose. If it is not yet installed on your machine, please follow these instructions: <https://docs.docker.com/engine/install/>

We offer multiple ways to execute Sawfish with docker. Each method differentiates in the ability to customize the output.

<details>
<summary>1. Master Script</summary>

The Master Script is the least customizable, but with one command, the following things will be done:

1. Install all needed systems (Maven, Metanome, Python)
2. Fetch all needed input data for Sawfish
3. Execution of the Sawfish Algorithm for all the input data (Can take <span style="color:red">multiple hours</span> to finish)
4. Generation of all the plots & graphs that can be found in the paper (After the execution visible in `paper/graphs/` directory)
5. Full regeneration of the paper with all new statistics, graphs & plots (After the execution visible in `paper/reproduced_paper.pdf`)

The master script can be executed with the command `docker-compose run sawfish-master`.
</details>

<details>
<summary>2. Metanome CLI</summary>
</details>
<details>
<summary>3. Metanome UI</summary>
Metanome is a convenient web platform, that you run locally. It provides a fresh view on data profiling and allows you to execute Sawfish in a more visual way. To use the Metanome UI, follow these instructions:

1. As Sawfish was initially build with the Metanome Web UI, create the main Sawfish image with `docker build -t sawfish .`.
2. Start a container by running `docker run -d -p 8080:8080 -p 8081:8081 sawfish`.
3. Now, open `localhost:8080` in your browser. You should now be able to see Metanome.
4. To get to know how to use Sawfish in Metanome, use the following video as reference:

It is not supported to generate the
<span style="color:red"> Insert Video here <span>
</details>

### Manual Installation
