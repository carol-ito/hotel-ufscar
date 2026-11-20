export type Perfil = "GESTAO" | "RECEPCAO";
export type StatusReserva = "PENDENTE" | "CONFIRMADA" | "EM_ANDAMENTO" | "ENCERRADA" | "CANCELADA";
export type StatusAcomodacao = "LIVRE" | "RESERVADO" | "OCUPADO";
export type TipoDocumento = "CPF" | "RG" | "PASSAPORTE" | "OUTRO";

export interface Usuario { id: number; nome: string; email: string; perfil: Perfil }
export interface Token { access_token: string; token_type: string; expires_in: number; usuario: Usuario }

export interface Pagina<T> { itens: T[]; total: number; limite: number; offset: number }

export interface Hospede {
  id: number; nome: string; documento_tipo: TipoDocumento; documento_numero: string;
  email: string | null; telefone: string | null; criado_em: string;
}
export interface HospedeForm {
  nome: string; documento_tipo: TipoDocumento; documento_numero: string; email: string; telefone: string;
}
export interface HospedeResumo { id: number; nome: string; documento_tipo: TipoDocumento; documento_numero: string }

export interface Categoria { id: number; nome: string; descricao: string | null }
export interface Caracteristica { id: number; nome: string }
/** Valores monetários chegam como string decimal ("150.00") para não perder precisão. */
export interface Acomodacao {
  id: number; numero: string; categoria: Categoria; capacidade: number; valor_diaria: string;
  status: StatusAcomodacao; ativo: boolean; caracteristicas: Caracteristica[];
}
export interface AcomodacaoForm {
  numero: string; categoria_id: number; capacidade: number; valor_diaria: string; caracteristica_ids: number[];
}
export interface Disponivel { acomodacao: Acomodacao; noites: number; valor_total: string }

export interface ReservaMapa { id: number; hospede_nome: string; data_entrada: string; data_saida: string; status: StatusReserva }
export interface MapaLinha { acomodacao: { id: number; numero: string; capacidade: number }; reservas: ReservaMapa[] }

export type AcaoReserva = "alterar" | "confirmar" | "cancelar";
export interface Reserva {
  id: number; hospede: HospedeResumo; acomodacao: { id: number; numero: string; capacidade: number };
  data_entrada: string; data_saida: string; noites: number; qtd_hospedes: number; status: StatusReserva;
  valor_diaria: string; valor_total: string; motivo_cancelamento: string | null; criada_em: string;
  confirmada_em: string | null; cancelada_em: string | null; checkin_em: string | null; checkout_em: string | null;
  acoes_permitidas: AcaoReserva[];
}
export interface NovaReserva {
  hospede_id: number; acomodacao_id: number; data_entrada: string; data_saida: string; qtd_hospedes: number;
}
