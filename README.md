# Regex to DFA

This is a project that converts a regex expression (with limited operators) into a DFA. The user has a json file for automated testing and a choice for self-testing.

## Project Structure
The program opens the json file and takes the regex expression from there. Then it adds the concatenation operator into the expression. After that, using the **Shunting Yard Algorithm**, we get the postfix notation, that is afterwards used to create a **Binary Tree** corresponding to the expression. Afterwards, we use the **Thompson Algorithm** to get the **NFA** from the tree. And last but not least, we convert the **NFA** to **DFA** using the **Subset  Construction**.

### Bibliography
[Shunting Yard Algorithm](https://blog.cernera.me/converting-regular-expressions-to-postfix-notation-with-the-shunting-yard-algorithm/)
[Thompson construction](https://en.wikipedia.org/wiki/Thompson%27s_construction)
[NFA to DFA](https://www.youtube.com/watch?v=jMxuL4Xzi_A)
