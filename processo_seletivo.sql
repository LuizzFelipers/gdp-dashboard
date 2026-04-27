

CREATE DATABASE processso_seletivo

USE processo_seletivo

 /*Query número 1: buscando as operadoras com:

a descrição = EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS  DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR

e com as maiores despesas*/

SELECT 
	TOP(10)*,
	(VL_SALDO_FINAL - VL_SALDO_INICIAL) as 'Despesas_totais'
FROM
	demonstracoe_totais_dados
WHERE descricao like '%EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS  DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR%' 
ORDER BY (VL_SALDO_FINAL - VL_SALDO_INICIAL) DESC


/* Query Número 2: buscando as operadoras com: 

a descrição = EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS  DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR;

com as maiores despesas;

no ano de 2024.*/

SELECT
	TOP(10)*,
	(VL_SALDO_FINAL - VL_SALDO_INICIAL) as 'Despesas_totais'
FROM
	demonstracoe_totais_dados
WHERE descricao like '%EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS  DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR%' and DATA between '2024-01-01' and '2024--12-31'
ORDER BY (VL_SALDO_FINAL - VL_SALDO_INICIAL) DESC




































































































































