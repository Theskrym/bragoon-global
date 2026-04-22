1. trocar o frontend2 para usar essa paleta de cores:

Background geral: #d3c5aa (bege/marrom claro)
Header/Navbar: #251708 (marrom escuro)
Texto dourado: #f7e07e (amarelo/dourado)
Hover dourado: #b08c43 (laranja/marrom)
Menu bar: #34495e (azul-cinza escuro)
Dropdown menu: #251708 (marrom escuro)
Dropdown hover: #3d566e
White: #fff
Texto escuro: #2c3e50


2. guardar os dados de todos os produtos que estejam vendendo o mesmo item,
ex.: "https://www.kabum.com.br/produto/320799/processador-amd-ryzen-5-5500-3-6ghz-4-2ghz-max-turbo-cache-19mb-am4-sem-video-100-100000457box" e "https://www.kabum.com.br/produto/356695/processador-amd-ryzen-5-5500-3-6ghz-cache-16mb-hexa-core-12-threads-am4-100-100000457box" estão vendendo o mesmo produto, então ao invés de aparecer 2 vezes ryzen 5 5500, aparecer só uma vez com o preço mais baixo, e quando eu abrir os detalhes do produto deve aparecer uma lista com todas as opçoes, que deve ser resumida as 5 opçoes mais baratas, e ela deve ter um botão "mostrar mais..." para mostrar a lista inteira, e eu quero que todos os produtos tenham um grafico, que mostre o preço médio, menor preço, e maior preço no ultimo ano daquele produto em especifico, e deve ser atualizado sempre que um novo daquele mesmo produto for adicionado a lista, e deve ter a data com quando foi atualizado, deve ser feito um grafico com no máximo 360 pontos(o grafico precisa ser no x=data e y=preço, e o deve ser um grafico com 3 linhas)

3. eu quero criar um sistema que o usuário possa criar "alertas" para dar trigger no navegador para mandar uma notificação quando um produto que o usuario escolher chegar a um preço que o usuario escolher.

4. configurar o banco de dados para ter todas as coisas nescessárias para que tudo mencionado seja possivel.

5. Atualizar scraper para popular ProductGroup e ProductVariant

6. Testar fluxo:
    - Ver produtos deduplilicados
    - Criar alerta
    - Receber notificação