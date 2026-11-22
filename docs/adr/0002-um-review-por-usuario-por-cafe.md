# Um review por usuário por café

Cada usuário tem **no máximo um review por café**. Se ele mudar de opinião,
edita o review existente: na página do café, o botão "Avaliar" vira "Editar
minha avaliação". Assim um único usuário não consegue inflar ou derrubar a
nota agregada. Tentar criar um segundo review para o mesmo café é um erro de
domínio. Consideramos permitir vários reviews (um por preparo, por exemplo),
mas isso exigiria decidir qual deles entra na média.
