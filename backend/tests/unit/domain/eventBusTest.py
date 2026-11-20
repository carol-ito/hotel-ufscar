from app.domain.reservaObserver import CheckInRealizado, EventBus, ReservaCancelada, ReservaCriada


class EventBusTest:
    def test_entrega_o_evento_a_todos_os_assinantes_na_ordem(self):
        bus, recebidos = EventBus(), []
        bus.subscribe(ReservaCriada, lambda e: recebidos.append(("a", e)))
        bus.subscribe(ReservaCriada, lambda e: recebidos.append(("b", e)))
        evento = ReservaCriada(1, 2)
        bus.publish(evento)
        assert recebidos == [("a", evento), ("b", evento)]

    def test_so_entrega_para_assinantes_do_mesmo_tipo(self):
        bus, recebidos = EventBus(), []
        bus.subscribe(ReservaCancelada, recebidos.append)
        bus.publish(ReservaCriada(1, 2))
        assert recebidos == []

    def test_publicar_sem_assinantes_nao_falha(self):
        EventBus().publish(CheckInRealizado(1, 1))

    def test_excecao_do_assinante_sobe_para_quem_publicou(self):
        bus = EventBus()
        def quebra(_): raise RuntimeError("falhou")
        bus.subscribe(ReservaCriada, quebra)
        try:
            bus.publish(ReservaCriada(1, 1))
        except RuntimeError as e:
            assert str(e) == "falhou"
        else:
            raise AssertionError("a exceção devia propagar para derrubar a transação")
